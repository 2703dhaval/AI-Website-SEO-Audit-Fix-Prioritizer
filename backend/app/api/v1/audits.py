from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.audit import Audit
from app.models.crawled_page import CrawledPage
from app.models.issue import SEOIssue
from app.schemas.audit import (
    AuditComparisonResponse,
    AuditCreate,
    AuditResponse,
    AuditSummaryResponse,
)
from app.schemas.health import ProgressResponse
from app.services.audit_service import (
    ACTIVE_PROGRESS,
    cancel_audit_service,
    start_audit_service,
)

router = APIRouter()


@router.get("", response_model=list[AuditResponse])
def list_audits(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    audits = (
        db.query(Audit).order_by(desc(Audit.created_at)).offset(skip).limit(limit).all()
    )
    return audits


@router.post("", response_model=AuditResponse, status_code=status.HTTP_201_CREATED)
def create_audit(audit_in: AuditCreate, db: Session = Depends(get_db)):
    try:
        audit = start_audit_service(
            db=db,
            url=str(audit_in.url),
            audit_name=audit_in.audit_name,
            max_pages=audit_in.max_pages or settings.DEFAULT_CRAWL_PAGES,
            max_depth=audit_in.max_depth or settings.DEFAULT_CRAWL_DEPTH,
            exclude_patterns=audit_in.exclude_patterns,
            crawl_delay=audit_in.crawl_delay_seconds or settings.REQUEST_DELAY_SECONDS,
            allow_test_mode=settings.ALLOW_LOCAL_TEST_DOMAINS,
        )
        return audit
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate audit: {e!s}",
        )


@router.get("/{audit_id}", response_model=AuditResponse)
def get_audit(audit_id: str, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return audit


@router.get("/{audit_id}/progress", response_model=ProgressResponse)
def get_audit_progress(audit_id: str, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    # In-memory live progress
    mem = ACTIVE_PROGRESS.get(audit_id)
    if mem:
        return ProgressResponse(
            audit_id=audit_id,
            status=mem.get("status", audit.status),
            pages_discovered=mem.get("pages_discovered", audit.total_discovered_pages),
            pages_crawled=mem.get("pages_crawled", audit.total_crawled_pages),
            pages_remaining=mem.get("pages_remaining", 0),
            current_stage=mem.get("current_stage", "Running audit checks"),
            issues_detected_so_far=mem.get("issues_detected_so_far", 0),
            latest_event=mem.get("latest_event"),
        )

    # Completed or inactive audit fallback
    return ProgressResponse(
        audit_id=audit_id,
        status=audit.status,
        pages_discovered=audit.total_discovered_pages,
        pages_crawled=audit.total_crawled_pages,
        pages_remaining=0,
        current_stage="Audit complete" if audit.status == "completed" else audit.status,
        issues_detected_so_far=len(audit.issues),
        latest_event=audit.status,
    )


@router.post("/{audit_id}/cancel")
def cancel_audit(audit_id: str, db: Session = Depends(get_db)):
    success = cancel_audit_service(db, audit_id)
    if not success:
        raise HTTPException(
            status_code=404, detail="Audit not found or could not be cancelled"
        )
    return {
        "message": "Audit cancellation requested successfully",
        "audit_id": audit_id,
    }


@router.delete("/{audit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_audit(audit_id: str, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    db.delete(audit)
    db.commit()


@router.get("/{audit_id}/summary", response_model=AuditSummaryResponse)
def get_audit_summary(audit_id: str, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    pages = db.query(CrawledPage).filter(CrawledPage.audit_id == audit_id).all()
    issues = (
        db.query(SEOIssue)
        .filter(SEOIssue.audit_id == audit_id)
        .order_by(desc(SEOIssue.priority_score))
        .all()
    )

    sev_breakdown = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "informational": 0,
    }
    cat_breakdown = {
        "crawlability": 0,
        "on_page": 0,
        "internal_linking": 0,
        "structured_data": 0,
        "performance": 0,
        "duplicates": 0,
    }

    for iss in issues:
        sev = iss.severity.lower()
        if sev in sev_breakdown:
            sev_breakdown[sev] += 1
        cat = iss.category.lower()
        if cat in cat_breakdown:
            cat_breakdown[cat] += 1

    idx_breakdown = {
        "indexable": 0,
        "noindex": 0,
        "canonicalized": 0,
        "error": 0,
        "blocked_by_robots": 0,
    }
    http_breakdown = {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0}

    for p in pages:
        stat = p.indexability_status or "indexable"
        if stat in idx_breakdown:
            idx_breakdown[stat] += 1
        else:
            idx_breakdown["indexable"] += 1

        code = p.http_status
        if 200 <= code < 300:
            http_breakdown["2xx"] += 1
        elif 300 <= code < 400:
            http_breakdown["3xx"] += 1
        elif 400 <= code < 500:
            http_breakdown["4xx"] += 1
        elif 500 <= code < 600:
            http_breakdown["5xx"] += 1

    top_fixes = [
        {
            "id": iss.id,
            "title": iss.title,
            "severity": iss.severity,
            "priority_score": iss.priority_score,
            "category": iss.category,
            "suggested_fix": iss.suggested_fix,
            "affected_page_count": iss.affected_page_count,
            "estimated_effort": iss.estimated_effort,
        }
        for iss in issues[:6]
    ]

    # Baseline theoretical checks count (e.g. 24 standard checks)
    total_checks_evaluated = 24
    passed_checks = max(0, total_checks_evaluated - len(issues))

    return AuditSummaryResponse(
        audit=audit,
        health_score=audit.seo_health_score,
        total_pages=len(pages),
        total_issues=len(issues),
        severity_breakdown=sev_breakdown,
        category_breakdown=cat_breakdown,
        top_priority_fixes=top_fixes,
        passed_checks_count=passed_checks,
        indexability_breakdown=idx_breakdown,
        http_status_breakdown=http_breakdown,
    )


@router.get(
    "/{audit_id}/compare/{other_audit_id}", response_model=AuditComparisonResponse
)
def compare_audits(audit_id: str, other_audit_id: str, db: Session = Depends(get_db)):
    summary1 = get_audit_summary(audit_id, db)
    summary2 = get_audit_summary(other_audit_id, db)

    issues1 = {
        iss.issue_code: iss
        for iss in db.query(SEOIssue).filter(SEOIssue.audit_id == audit_id).all()
    }
    issues2 = {
        iss.issue_code: iss
        for iss in db.query(SEOIssue).filter(SEOIssue.audit_id == other_audit_id).all()
    }

    resolved = [
        {"issue_code": code, "title": iss.title, "severity": iss.severity}
        for code, iss in issues1.items()
        if code not in issues2
    ]
    new_issues = [
        {"issue_code": code, "title": iss.title, "severity": iss.severity}
        for code, iss in issues2.items()
        if code not in issues1
    ]

    return AuditComparisonResponse(
        audit1=summary1,
        audit2=summary2,
        health_score_delta=round(summary2.health_score - summary1.health_score, 1),
        total_issues_delta=summary2.total_issues - summary1.total_issues,
        new_issues=new_issues,
        resolved_issues=resolved,
    )
