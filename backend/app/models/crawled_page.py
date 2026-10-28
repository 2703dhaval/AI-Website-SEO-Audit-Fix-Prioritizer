import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CrawledPage(Base):
    __tablename__ = "crawled_pages"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    audit_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("audits.id", ondelete="CASCADE"), index=True
    )

    requested_url: Mapped[str] = mapped_column(Text, nullable=False)
    final_url: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    canonical_url: Mapped[str] = mapped_column(Text, nullable=True)

    http_status: Mapped[int] = mapped_column(Integer, default=200, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=True)
    meta_description: Mapped[str] = mapped_column(Text, nullable=True)
    h1_data: Mapped[dict] = mapped_column(JSON, default=list)  # list of H1 string texts

    language: Mapped[str] = mapped_column(String(50), nullable=True)
    robots_directives: Mapped[str] = mapped_column(
        String(255), nullable=True
    )  # e.g., "noindex, follow"

    word_count: Mapped[int] = mapped_column(Integer, default=0)
    internal_link_count: Mapped[int] = mapped_column(Integer, default=0)
    external_link_count: Mapped[int] = mapped_column(Integer, default=0)

    response_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    response_size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    crawl_depth: Mapped[int] = mapped_column(Integer, default=0)

    indexability_status: Mapped[str] = mapped_column(
        String(50), default="indexable", index=True
    )
    # indexable, noindex, blocked_by_robots, canonicalized, error, redirected

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    audit = relationship("Audit", back_populates="pages")
    evidences = relationship(
        "IssueEvidence", back_populates="page", cascade="all, delete-orphan"
    )
