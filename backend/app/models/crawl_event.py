import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CrawlEvent(Base):
    __tablename__ = "crawl_events"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    audit_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("audits.id", ondelete="CASCADE"), index=True
    )

    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # start, crawl_page, error, info, complete, cancel
    url: Mapped[str] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)

    audit = relationship("Audit", back_populates="events")
