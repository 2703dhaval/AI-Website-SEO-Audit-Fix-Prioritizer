from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.audit import AuditResponse
from app.services.sample_report_data import seed_sample_company_audit

router = APIRouter()


@router.get("/sample-report", response_model=AuditResponse)
def get_or_seed_sample_report(db: Session = Depends(get_db)):
    """
    Retrieves or seeds the official Scalezix company sample SEO audit report.
    """
    audit = seed_sample_company_audit(db)
    return audit
