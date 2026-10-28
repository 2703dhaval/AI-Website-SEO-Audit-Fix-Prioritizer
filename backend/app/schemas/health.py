from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status: str
    version: str
    database: str
    environment: str


class ProgressResponse(BaseModel):
    audit_id: str
    status: str
    pages_discovered: int
    pages_crawled: int
    pages_remaining: int
    current_stage: str
    issues_detected_so_far: int
    latest_event: str | None = None
