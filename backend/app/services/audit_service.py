import threading
import uuid
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.core.ssrf import validate_url_ssrf
from app.crawler.crawler import WebCrawler
from app.db import session as db_session_module
from app.models.audit import Audit
from app.models.crawl_event import CrawlEvent
from app.models.crawled_page import CrawledPage
from app.models.issue import IssueEvidence, SEOIssue
from app.prioritization.engine import (
    calculate_priority_score,
    calculate_scope,
    generate_priority_reason,
)
from app.prioritization.health_score import calculate_seo_health_score
from app.seo_checks.runner import run_all_seo_checks

# Global in-memory tracking for active audit states & cancellation flags
ACTIVE_PROGRESS: dict[str, dict[str, Any]] = {}
CANCELLATION_FLAGS: dict[str, bool] = {}


def run_audit_background_task(audit_id: str, allow_test_mode: bool = False):
    """
    Background worker thread function that crawls the website,
    executes SEO detection checks, computes prioritization & health score,
    and updates the database.
    """
    db: Session = db_session_module.SessionLocal()
    try:
        audit = db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            return

        audit.status = "running"
        audit.started_at = datetime.now(UTC)
        db.commit()

        config = audit.configuration or {}
        max_pages = config.get("max_pages", 25)
        max_depth = config.get("max_depth", 3)
        crawl_delay = config.get("crawl_delay", 0.5)
        exclude_patterns = config.get("exclude_patterns", [])

        ACTIVE_PROGRESS[audit_id] = {
            "status": "running",
            "pages_discovered": 1,
            "pages_crawled": 0,
            "pages_remaining": 1,
            "current_stage": "Initializing crawler & verifying robots.txt",
            "issues_detected_so_far": 0,
            "latest_event": "Checking robots.txt policy",
        }

        def on_progress_callback(info: dict[str, Any]):
            crawled = info.get("pages_crawled", 0)
            discovered = info.get("pages_discovered", 1)
            remaining = max(0, min(discovered, max_pages) - crawled)
            ACTIVE_PROGRESS[audit_id] = {
                "status": "running",
                "pages_discovered": discovered,
                "pages_crawled": crawled,
                "pages_remaining": remaining,
                "current_stage": f"Crawling page {crawled}/{min(discovered, max_pages)}",
                "issues_detected_so_far": 0,
                "latest_event": f"Crawling {info.get('current_url', '')}",
            }

        def check_cancelled() -> bool:
            return CANCELLATION_FLAGS.get(audit_id, False)

        crawler = WebCrawler(
            start_url=audit.submitted_url,
            max_pages=max_pages,
            max_depth=max_depth,
            crawl_delay=crawl_delay,
            exclude_patterns=exclude_patterns,
            allow_test_mode=allow_test_mode,
            on_progress=on_progress_callback,
            is_cancelled=check_cancelled,
        )

        crawl_result = crawler.crawl()

        # Check if cancelled mid-crawl
        if check_cancelled() or crawl_result.get("status") == "cancelled":
            audit.status = "cancelled"
            audit.completed_at = datetime.now(UTC)
            audit.error_summary = "Audit was cancelled by the user."
            db.commit()
            if audit_id in ACTIVE_PROGRESS:
                ACTIVE_PROGRESS[audit_id]["status"] = "cancelled"
                ACTIVE_PROGRESS[audit_id]["current_stage"] = "Cancelled by user"
            return

        crawled_pages = crawl_result.get("crawled_pages", [])
        robots_summary = crawl_result.get("robots_summary", {})
        audit.crawl_policy_summary = robots_summary.get("summary", "")
        audit.total_discovered_pages = crawl_result.get(
            "total_discovered", len(crawled_pages)
        )
        audit.total_crawled_pages = len(crawled_pages)

        if audit_id in ACTIVE_PROGRESS:
            ACTIVE_PROGRESS[audit_id]["current_stage"] = (
                "Analyzing SEO rules & evaluating issue severity"
            )
            ACTIVE_PROGRESS[audit_id]["pages_crawled"] = len(crawled_pages)

        # Save crawled pages to database
        db_pages = []
        for p in crawled_pages:
            page_obj = CrawledPage(
                id=str(uuid.uuid4()),
                audit_id=audit.id,
                requested_url=p["requested_url"],
                final_url=p["final_url"],
                canonical_url=p.get("canonical_url"),
                http_status=p.get("http_status", 200),
                title=p.get("title"),
                meta_description=p.get("meta_description"),
                h1_data=p.get("h1_list", []),
                language=p.get("language"),
                robots_directives=p.get("robots_directives"),
                word_count=p.get("word_count", 0),
                internal_link_count=len(p.get("internal_links", [])),
                external_link_count=len(p.get("external_links", [])),
                response_time_ms=p.get("response_time_ms", 0.0),
                response_size_bytes=p.get("response_size_bytes", 0),
                crawl_depth=p.get("crawl_depth", 0),
                indexability_status=p.get("indexability_status", "indexable"),
            )
            db.add(page_obj)
            db_pages.append(page_obj)
        db.flush()

        # Step 3: Run SEO checks
        detected_checks = run_all_seo_checks(crawled_pages, robots_summary)

        # Step 4: Health Score & Prioritization
        health_score, score_breakdown = calculate_seo_health_score(
            detected_checks, len(crawled_pages)
        )
        audit.seo_health_score = health_score
        audit.scoring_version = "v1.0"

        # Save issues and evidences
        for chk in detected_checks:
            scope = calculate_scope(chk.affected_page_count, len(crawled_pages))
            priority = calculate_priority_score(
                impact=chk.impact,
                scope=scope,
                confidence=chk.confidence,
                effort=chk.estimated_effort,
            )
            reason = generate_priority_reason(
                severity=chk.severity,
                priority_score=priority,
                impact=chk.impact,
                scope=scope,
                effort=chk.estimated_effort,
            )

            issue_obj = SEOIssue(
                id=str(uuid.uuid4()),
                audit_id=audit.id,
                issue_code=chk.issue_code,
                title=chk.title,
                category=chk.category,
                severity=chk.severity,
                priority_score=priority,
                impact=chk.impact,
                confidence=chk.confidence,
                estimated_effort=chk.estimated_effort,
                description=chk.description,
                why_it_matters=chk.why_it_matters,
                suggested_fix=chk.suggested_fix,
                example_fix=chk.example_fix,
                priority_reason=reason,
                status="open",
                affected_page_count=chk.affected_page_count,
            )
            db.add(issue_obj)
            db.flush()

            for ev in chk.evidences:
                evidence_obj = IssueEvidence(
                    id=str(uuid.uuid4()),
                    issue_id=issue_obj.id,
                    page_url=ev.page_url,
                    observed_value=ev.observed_value,
                    expected_value=ev.expected_value,
                    evidence_snippet=ev.evidence_snippet,
                    evidence_type=ev.evidence_type,
                    explanation=ev.explanation,
                )
                db.add(evidence_obj)

        # Log events
        for ev in crawl_result.get("events", []):
            db.add(
                CrawlEvent(
                    id=str(uuid.uuid4()),
                    audit_id=audit.id,
                    event_type=ev.get("event_type", "info"),
                    url=ev.get("url"),
                    message=ev.get("message", ""),
                )
            )

        audit.status = "completed"
        audit.completed_at = datetime.now(UTC)
        db.commit()

        if audit_id in ACTIVE_PROGRESS:
            ACTIVE_PROGRESS[audit_id] = {
                "status": "completed",
                "pages_discovered": audit.total_discovered_pages,
                "pages_crawled": audit.total_crawled_pages,
                "pages_remaining": 0,
                "current_stage": "Audit complete! All issues prioritized.",
                "issues_detected_so_far": len(detected_checks),
                "latest_event": "Finished",
            }

    except Exception as e:
        db.rollback()
        audit = db.query(Audit).filter(Audit.id == audit_id).first()
        if audit:
            audit.status = "failed"
            audit.error_summary = str(e)
            audit.completed_at = datetime.now(UTC)
            db.commit()
        if audit_id in ACTIVE_PROGRESS:
            ACTIVE_PROGRESS[audit_id] = {
                "status": "failed",
                "pages_discovered": 0,
                "pages_crawled": 0,
                "pages_remaining": 0,
                "current_stage": f"Error: {e!s}",
                "issues_detected_so_far": 0,
                "latest_event": "Failed",
            }
    finally:
        db.close()
        CANCELLATION_FLAGS.pop(audit_id, None)


def start_audit_service(
    db: Session,
    url: str,
    audit_name: str | None = None,
    max_pages: int = 25,
    max_depth: int = 3,
    exclude_patterns: list | None = None,
    crawl_delay: float = 0.5,
    allow_test_mode: bool = False,
) -> Audit:
    """
    Validates URL safely, creates the Audit record in database,
    and initiates the background crawl worker.
    """
    # SSRF & URL validation
    is_safe, resolved_ip, err = validate_url_ssrf(url, allow_test_mode=allow_test_mode)
    if not is_safe:
        raise ValueError(f"URL failed security validation: {err}")

    parsed = urlparse(url)
    normalized_domain = parsed.hostname or url

    audit_id = str(uuid.uuid4())
    audit = Audit(
        id=audit_id,
        audit_name=audit_name or f"Audit of {normalized_domain}",
        submitted_url=url,
        normalized_domain=normalized_domain,
        status="queued",
        configuration={
            "max_pages": max_pages,
            "max_depth": max_depth,
            "exclude_patterns": exclude_patterns or [],
            "crawl_delay": crawl_delay,
        },
        total_discovered_pages=1,
        total_crawled_pages=0,
        seo_health_score=100.0,
        scoring_version="v1.0",
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)

    ACTIVE_PROGRESS[audit_id] = {
        "status": "queued",
        "pages_discovered": 1,
        "pages_crawled": 0,
        "pages_remaining": 1,
        "current_stage": "Queued for audit execution",
        "issues_detected_so_far": 0,
        "latest_event": "Queued",
    }

    # Start asynchronous background thread worker
    worker_thread = threading.Thread(
        target=run_audit_background_task, args=(audit_id, allow_test_mode), daemon=True
    )
    worker_thread.start()

    return audit


def cancel_audit_service(db: Session, audit_id: str) -> bool:
    """Signals cooperative cancellation to the active audit crawler."""
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        return False
    if audit.status in ("completed", "failed", "cancelled"):
        return True

    CANCELLATION_FLAGS[audit_id] = True
    audit.status = "cancelled"
    db.commit()

    if audit_id in ACTIVE_PROGRESS:
        ACTIVE_PROGRESS[audit_id]["status"] = "cancelled"
        ACTIVE_PROGRESS[audit_id]["current_stage"] = "Audit cancelled by user"

    return True
