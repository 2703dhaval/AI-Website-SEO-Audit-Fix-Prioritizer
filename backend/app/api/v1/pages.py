from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.crawled_page import CrawledPage
from app.models.issue import IssueEvidence
from app.schemas.crawled_page import CrawledPageListResponse, CrawledPageResponse

router = APIRouter()


@router.get("/{audit_id}/pages", response_model=CrawledPageListResponse)
def list_crawled_pages(
    audit_id: str,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    status_filter: str | None = None,
    search: str | None = None,
):
    query = db.query(CrawledPage).filter(CrawledPage.audit_id == audit_id)

    if status_filter:
        query = query.filter(CrawledPage.indexability_status == status_filter)

    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            (CrawledPage.final_url.ilike(search_fmt))
            | (CrawledPage.title.ilike(search_fmt))
        )

    total = query.count()
    offset = (page - 1) * limit
    items = (
        query.order_by(CrawledPage.crawl_depth, CrawledPage.final_url)
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Pre-fetch issue counts per page URL
    page_urls = [p.final_url for p in items]
    issue_counts_by_url = {}
    if page_urls:
        counts = (
            db.query(IssueEvidence.page_url, func.count(IssueEvidence.id))
            .filter(IssueEvidence.page_url.in_(page_urls))
            .group_by(IssueEvidence.page_url)
            .all()
        )
        issue_counts_by_url = {url: cnt for url, cnt in counts}

    result_items = []
    for item in items:
        resp = CrawledPageResponse.model_validate(item)
        resp.issue_count = issue_counts_by_url.get(item.final_url, 0)
        result_items.append(resp)

    total_pages = (total + limit - 1) // limit if total > 0 else 1
    return CrawledPageListResponse(
        items=result_items, total=total, page=page, limit=limit, pages=total_pages
    )
