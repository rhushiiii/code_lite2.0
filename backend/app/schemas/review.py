from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class Issue(BaseModel):
    file: str = Field(default="unknown")
    line: int | None = None
    severity: Literal["low", "medium", "high"] = "low"
    message: str
    code_snippet: str | None = None
    suggestion: str | None = None


class ReviewRequest(BaseModel):
    repo_owner: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.-]+$")
    repo_name: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.-]+$")
    pr_number: PositiveInt
    github_token: str | None = Field(default=None, min_length=20, max_length=255)


class ReviewResult(BaseModel):
    issues: list[Issue] = Field(default_factory=list)


class ReviewResponse(BaseModel):
    id: int
    repo_name: str
    pr_number: int
    result_json: dict
    severity_summary: dict[str, int]
    changed_files: list[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
