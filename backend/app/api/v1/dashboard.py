from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit import Audit
from app.models.issue import SEOIssue
from app.schemas.audit import AuditResponse

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)) -> dict[str, Any]:
    total_audits = db.query(func.count(Audit.id)).scalar() or 0
    unique_domains = (
        db.query(func.count(func.distinct(Audit.normalized_domain))).scalar() or 0
    )

    total_issues = db.query(func.count(SEOIssue.id)).scalar() or 0
    critical_issues = (
        db.query(func.count(SEOIssue.id))
        .filter(SEOIssue.severity == "critical")
        .scalar()
        or 0
    )
    high_issues = (
        db.query(func.count(SEOIssue.id)).filter(SEOIssue.severity == "high").scalar()
        or 0
    )

    avg_score_raw = (
        db.query(func.avg(Audit.seo_health_score))
        .filter(Audit.status == "completed")
        .scalar()
    )
    avg_health_score = (
        round(float(avg_score_raw), 1) if avg_score_raw is not None else 100.0
    )

    recent_audits = db.query(Audit).order_by(desc(Audit.created_at)).limit(6).all()

    # Severity distribution
    sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "informational": 0}
    sev_query = (
        db.query(SEOIssue.severity, func.count(SEOIssue.id))
        .group_by(SEOIssue.severity)
        .all()
    )
    for sev, cnt in sev_query:
        if sev in sev_counts:
            sev_counts[sev] = cnt

    # Category distribution
    cat_counts = {
        "crawlability": 0,
        "on_page": 0,
        "internal_linking": 0,
        "structured_data": 0,
        "performance": 0,
        "duplicates": 0,
    }
    cat_query = (
        db.query(SEOIssue.category, func.count(SEOIssue.id))
        .group_by(SEOIssue.category)
        .all()
    )
    for cat, cnt in cat_query:
        if cat in cat_counts:
            cat_counts[cat] = cnt

    return {
        "total_audits": total_audits,
        "websites_audited": unique_domains,
        "total_issues": total_issues,
        "critical_issues": critical_issues,
        "high_issues": high_issues,
        "critical_and_high_issues": critical_issues + high_issues,
        "avg_health_score": avg_health_score,
        "recent_audits": [AuditResponse.model_validate(a) for a in recent_audits],
        "severity_distribution": sev_counts,
        "category_distribution": cat_counts,
    }
