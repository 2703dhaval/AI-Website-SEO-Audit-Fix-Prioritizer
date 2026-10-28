from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.issue import SEOIssue
from app.schemas.issue import IssueStatusUpdate, SEOIssueListResponse, SEOIssueResponse

router = APIRouter()


@router.get("/{audit_id}/issues", response_model=SEOIssueListResponse)
def list_audit_issues(
    audit_id: str,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    severity: str | None = None,
    category: str | None = None,
    status_filter: str | None = None,
    search: str | None = None,
    sort_by: str = Query(
        "priority_score", pattern="^(priority_score|severity|title|created_at)$"
    ),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
):
    query = db.query(SEOIssue).filter(SEOIssue.audit_id == audit_id)

    if severity:
        query = query.filter(SEOIssue.severity == severity.lower())
    if category:
        query = query.filter(SEOIssue.category == category.lower())
    if status_filter:
        query = query.filter(SEOIssue.status == status_filter.lower())
    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            (SEOIssue.title.ilike(search_fmt))
            | (SEOIssue.description.ilike(search_fmt))
            | (SEOIssue.suggested_fix.ilike(search_fmt))
        )

    order_col = getattr(SEOIssue, sort_by, SEOIssue.priority_score)
    query = query.order_by(desc(order_col) if sort_dir == "desc" else asc(order_col))

    total = query.count()
    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    total_pages = (total + limit - 1) // limit if total > 0 else 1
    return SEOIssueListResponse(
        items=items, total=total, page=page, limit=limit, pages=total_pages
    )


@router.get("/{audit_id}/issues/{issue_id}", response_model=SEOIssueResponse)
def get_issue_detail(audit_id: str, issue_id: str, db: Session = Depends(get_db)):
    issue = (
        db.query(SEOIssue)
        .filter(SEOIssue.audit_id == audit_id, SEOIssue.id == issue_id)
        .first()
    )
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue


@router.patch("/{audit_id}/issues/{issue_id}", response_model=SEOIssueResponse)
def update_issue_status(
    audit_id: str,
    issue_id: str,
    status_update: IssueStatusUpdate,
    db: Session = Depends(get_db),
):
    valid_statuses = {"open", "in_progress", "resolved", "ignored"}
    new_status = status_update.status.lower()
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{status_update.status}'. Must be one of {valid_statuses}",
        )

    issue = (
        db.query(SEOIssue)
        .filter(SEOIssue.audit_id == audit_id, SEOIssue.id == issue_id)
        .first()
    )
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    issue.status = new_status
    db.commit()
    db.refresh(issue)
    return issue
