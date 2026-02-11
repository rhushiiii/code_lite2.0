from pydantic import BaseModel, Field


class PendingPullRequest(BaseModel):
    number: int
    title: str
    html_url: str
    state: str
    draft: bool
    created_at: str
    updated_at: str
    author: str | None = None


class RepoPendingPulls(BaseModel):
    owner: str
    repo: str
    full_name: str
    private: bool
    html_url: str
    pending_pr_count: int = 0
    pending_pull_requests: list[PendingPullRequest] = Field(default_factory=list)


class ReposPendingPullsResponse(BaseModel):
    total_repos_scanned: int
    repos: list[RepoPendingPulls] = Field(default_factory=list)
