from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CrawledPageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    audit_id: str
    requested_url: str
    final_url: str
    canonical_url: str | None = None
    http_status: int
    title: str | None = None
    meta_description: str | None = None
    h1_data: list[str] | None = None
    language: str | None = None
    robots_directives: str | None = None
    word_count: int = 0
    internal_link_count: int = 0
    external_link_count: int = 0
    response_time_ms: float = 0.0
    response_size_bytes: int = 0
    crawl_depth: int = 0
    indexability_status: str
    created_at: datetime
    issue_count: int | None = 0


class CrawledPageListResponse(BaseModel):
    items: list[CrawledPageResponse]
    total: int
    page: int
    limit: int
    pages: int
