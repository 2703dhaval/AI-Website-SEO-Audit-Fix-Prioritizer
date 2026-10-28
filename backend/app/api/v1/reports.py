from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit import Audit
from app.models.crawled_page import CrawledPage
from app.models.issue import SEOIssue
from app.reports.csv_export import generate_issues_csv
from app.reports.json_export import generate_audit_json
from app.reports.pdf_generator import generate_audit_pdf

router = APIRouter()


@router.get("/{audit_id}/export.csv")
def export_csv(audit_id: str, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    issues = (
        db.query(SEOIssue)
        .filter(SEOIssue.audit_id == audit_id)
        .order_by(SEOIssue.priority_score.desc())
        .all()
    )
    csv_content = generate_issues_csv(audit, issues)

    safe_domain = audit.normalized_domain.replace(".", "_")
    filename = f"seo_audit_{safe_domain}_{audit_id[:8]}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{audit_id}/export.json")
def export_json(audit_id: str, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    pages = db.query(CrawledPage).filter(CrawledPage.audit_id == audit_id).all()
    issues = (
        db.query(SEOIssue)
        .filter(SEOIssue.audit_id == audit_id)
        .order_by(SEOIssue.priority_score.desc())
        .all()
    )

    json_data = generate_audit_json(audit, pages, issues)
    return json_data


@router.get("/{audit_id}/report.pdf")
def export_pdf(audit_id: str, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    pages = db.query(CrawledPage).filter(CrawledPage.audit_id == audit_id).all()
    issues = (
        db.query(SEOIssue)
        .filter(SEOIssue.audit_id == audit_id)
        .order_by(SEOIssue.priority_score.desc())
        .all()
    )

    pdf_bytes = generate_audit_pdf(audit, pages, issues)
    safe_domain = audit.normalized_domain.replace(".", "_")
    filename = f"seo_report_{safe_domain}_{audit_id[:8]}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
