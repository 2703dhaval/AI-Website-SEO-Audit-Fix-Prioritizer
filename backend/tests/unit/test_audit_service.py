import pytest
from app.services.audit_service import start_audit_service, cancel_audit_service, ACTIVE_PROGRESS, CANCELLATION_FLAGS
from app.models.audit import Audit


class TestAuditService:
    def test_start_and_cancel_audit_service(self, db_session):
        audit = start_audit_service(
            db=db_session,
            url="http://127.0.0.1:8765",
            audit_name="Service Test Audit",
            max_pages=5,
            max_depth=1,
            allow_test_mode=True
        )
        assert audit.id is not None
        assert audit.status in ("queued", "running")

        # Test cancel
        cancelled = cancel_audit_service(db_session, audit.id)
        assert cancelled is True

        # Cancel on non-existent audit
        cancelled_none = cancel_audit_service(db_session, "nonexistent-id")
        assert cancelled_none is False
