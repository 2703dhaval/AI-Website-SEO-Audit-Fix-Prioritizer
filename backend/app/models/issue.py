import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SEOIssue(Base):
    __tablename__ = "seo_issues"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    audit_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("audits.id", ondelete="CASCADE"), index=True
    )

    issue_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # categories: crawlability, on_page, internal_linking, structured_data, performance, duplicates

    severity: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # critical, high, medium, low, informational

    priority_score: Mapped[float] = mapped_column(Float, default=50.0, index=True)
    impact: Mapped[float] = mapped_column(Float, default=0.5)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    estimated_effort: Mapped[float] = mapped_column(
        Float, default=0.3
    )  # 0.0 (trivial) to 1.0 (complex)

    description: Mapped[str] = mapped_column(Text, nullable=False)
    why_it_matters: Mapped[str] = mapped_column(Text, nullable=True)
    suggested_fix: Mapped[str] = mapped_column(Text, nullable=False)
    example_fix: Mapped[str] = mapped_column(Text, nullable=True)
    priority_reason: Mapped[str] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(50), default="open", index=True)
    # open, in_progress, resolved, ignored

    affected_page_count: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    audit = relationship("Audit", back_populates="issues")
    evidences = relationship(
        "IssueEvidence", back_populates="issue", cascade="all, delete-orphan"
    )


class IssueEvidence(Base):
    __tablename__ = "issue_evidences"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    issue_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("seo_issues.id", ondelete="CASCADE"), index=True
    )
    page_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("crawled_pages.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    page_url: Mapped[str] = mapped_column(Text, nullable=False)
    observed_value: Mapped[str] = mapped_column(Text, nullable=True)
    expected_value: Mapped[str] = mapped_column(Text, nullable=True)
    evidence_snippet: Mapped[str] = mapped_column(Text, nullable=True)
    evidence_type: Mapped[str] = mapped_column(String(50), default="html_element")
    explanation: Mapped[str] = mapped_column(Text, nullable=True)

    issue = relationship("SEOIssue", back_populates="evidences")
    page = relationship("CrawledPage", back_populates="evidences")
