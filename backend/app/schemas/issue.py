from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class IssueEvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    issue_id: str
    page_id: str | None = None
    page_url: str
    observed_value: str | None = None
    expected_value: str | None = None
    evidence_snippet: str | None = None
    evidence_type: str = "html_element"
    explanation: str | None = None


class SEOIssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    audit_id: str
    issue_code: str
    title: str
    category: str
    severity: str
    priority_score: float
    impact: float
    confidence: float
    estimated_effort: float
    description: str
    why_it_matters: str | None = None
    suggested_fix: str
    example_fix: str | None = None
    priority_reason: str | None = None
    status: str
    affected_page_count: int
    created_at: datetime
    evidences: list[IssueEvidenceResponse] | None = []


class SEOIssueListResponse(BaseModel):
    items: list[SEOIssueResponse]
    total: int
    page: int
    limit: int
    pages: int


class IssueStatusUpdate(BaseModel):
    status: str = Field(..., description="Status: open, in_progress, resolved, ignored")
