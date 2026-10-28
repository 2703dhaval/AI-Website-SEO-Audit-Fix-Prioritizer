import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Audit(Base):
    __tablename__ = "audits"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    audit_name: Mapped[str] = mapped_column(String(255), nullable=True)
    submitted_url: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_domain: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="queued", index=True
    )  # queued, running, completed, failed, cancelled
    configuration: Mapped[dict] = mapped_column(JSON, default=dict)

    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    error_summary: Mapped[str] = mapped_column(Text, nullable=True)

    total_discovered_pages: Mapped[int] = mapped_column(Integer, default=0)
    total_crawled_pages: Mapped[int] = mapped_column(Integer, default=0)

    seo_health_score: Mapped[float] = mapped_column(Float, default=100.0)
    scoring_version: Mapped[str] = mapped_column(String(50), default="v1.0")
    crawl_policy_summary: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    # Relationships
    pages = relationship(
        "CrawledPage",
        back_populates="audit",
        cascade="all, delete-orphan",
        order_by="CrawledPage.crawl_depth",
    )
    issues = relationship(
        "SEOIssue",
        back_populates="audit",
        cascade="all, delete-orphan",
        order_by="desc(SEOIssue.priority_score)",
    )
    events = relationship(
        "CrawlEvent",
        back_populates="audit",
        cascade="all, delete-orphan",
        order_by="CrawlEvent.timestamp",
    )
