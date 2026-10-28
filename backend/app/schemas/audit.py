from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuditCreate(BaseModel):
    url: str = Field(..., description="The website URL to audit (HTTP or HTTPS)")
    audit_name: str | None = Field(
        None, max_length=255, description="Optional custom label for this audit"
    )
    max_pages: int | None = Field(25, ge=1, le=100, description="Max pages to crawl")
    max_depth: int | None = Field(3, ge=1, le=5, description="Max crawl depth")
    exclude_patterns: list[str] | None = Field(
        default=[], description="Path regex/substrings to exclude"
    )
    crawl_delay_seconds: float | None = Field(0.5, ge=0.0, le=5.0)


class AuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    audit_name: str | None = None
    submitted_url: str
    normalized_domain: str
    status: str
    configuration: dict[str, Any] = {}
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_summary: str | None = None
    total_discovered_pages: int = 0
    total_crawled_pages: int = 0
    seo_health_score: float = 100.0
    scoring_version: str = "v1.0"
    crawl_policy_summary: str | None = None
    created_at: datetime


class AuditSummaryResponse(BaseModel):
    audit: AuditResponse
    health_score: float
    total_pages: int
    total_issues: int
    severity_breakdown: dict[str, int]
    category_breakdown: dict[str, int]
    top_priority_fixes: list[Any]
    passed_checks_count: int
    indexability_breakdown: dict[str, int]
    http_status_breakdown: dict[str, int]


class AuditComparisonResponse(BaseModel):
    audit1: AuditSummaryResponse
    audit2: AuditSummaryResponse
    health_score_delta: float
    total_issues_delta: int
    new_issues: list[Any]
    resolved_issues: list[Any]
