import json
import logging
import re
from typing import Any

import httpx
from pydantic import BaseModel

from app.core.config import get_settings
from app.schemas.review import Issue

settings = get_settings()
logger = logging.getLogger(__name__)


class LLMOutput(BaseModel):
    issues: list[Issue]


class LLMService:
    def __init__(self) -> None:
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL
        self.max_retries = settings.LLM_MAX_RETRIES

    async def analyze_diff(self, diff_text: str, changed_files: list[str]) -> dict[str, Any]:
        truncated_diff = diff_text[: settings.MAX_DIFF_CHARS]
        prompt = self._build_prompt(truncated_diff, changed_files)

        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                model_output = await self._call_ollama(prompt)
                parsed = self._parse_output(model_output)
                result = parsed.model_dump()
                result["changed_files"] = changed_files
                return result
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.warning("LLM parsing failed on attempt %s: %s", attempt, exc)

        logger.error("LLM analysis failed after retries: %s", last_error)
        return {
            "issues": [
                {
                    "file": "system",
                    "line": None,
                    "severity": "low",
                    "message": "Review completed with limited AI analysis due to LLM response error.",
                    "code_snippet": None,
                    "suggestion": "Retry in a minute or verify your Ollama model is running.",
                }
            ],
            "changed_files": changed_files,
        }

    def _build_prompt(self, diff_text: str, changed_files: list[str]) -> str:
        files_block = "\n".join(f"- {name}" for name in changed_files) if changed_files else "- none"

        return f"""
You are a principal code reviewer focusing on security and quality.
Analyze the provided git diff and return ONLY valid minified JSON with this exact schema:
{{
  "issues": [
    {{
      "file": "string",
      "line": 1,
      "severity": "low|medium|high",
      "message": "string",
      "code_snippet": "string",
      "suggestion": "string"
    }}
  ]
}}

Rules:
- Must detect: SQL injection risks, hardcoded secrets, performance problems, security flaws, and code quality issues.
- If no issues are found, return {{"issues":[]}}.
- `severity` must be one of: low, medium, high.
- Use line as integer when possible, otherwise null.
- Never include markdown, explanation, or extra keys.

Changed files:
{files_block}

Diff:
{diff_text}
""".strip()

    async def _call_ollama(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.1},
        }

        try:
            async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
                response = await client.post(url, json=payload)
        except httpx.RequestError as exc:
            raise RuntimeError("Failed to connect to Ollama") from exc

        if response.status_code >= 400:
            raise RuntimeError(f"Ollama request failed with status {response.status_code}")

        try:
            body = response.json()
        except ValueError as exc:
            raise RuntimeError("Ollama returned invalid JSON payload") from exc
        output = body.get("response", "").strip()
        if not output:
            raise RuntimeError("Empty response from Ollama")

        return output

    def _parse_output(self, raw_output: str) -> LLMOutput:
        data = self._safe_json_load(raw_output)

        if isinstance(data, list):
            data = {"issues": data}

        if not isinstance(data, dict) or "issues" not in data:
            raise ValueError("LLM output is missing 'issues'")

        issues = data.get("issues", [])
        if isinstance(issues, list):
            for issue in issues:
                if not isinstance(issue, dict):
                    continue
                if issue.get("severity") is not None:
                    issue["severity"] = str(issue["severity"]).lower()
                if issue.get("line") in ("", "null", "None"):
                    issue["line"] = None
                elif issue.get("line") is not None:
                    try:
                        issue["line"] = int(issue["line"])
                    except (TypeError, ValueError):
                        issue["line"] = None

        return LLMOutput.model_validate(data)

    @staticmethod
    def _safe_json_load(raw_text: str) -> Any:
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", raw_text)
            if not match:
                raise
            return json.loads(match.group(0))
