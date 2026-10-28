from typing import Any


def generate_audit_json(
    audit: Any, pages: list[Any], issues: list[Any]
) -> dict[str, Any]:
    """
    Constructs a comprehensive, machine-readable JSON export of the entire audit.
    """
    return {
        "audit_metadata": {
            "id": audit.id,
            "name": audit.audit_name,
            "submitted_url": audit.submitted_url,
            "domain": audit.normalized_domain,
            "status": audit.status,
            "seo_health_score": audit.seo_health_score,
            "scoring_version": audit.scoring_version,
            "total_discovered_pages": audit.total_discovered_pages,
            "total_crawled_pages": audit.total_crawled_pages,
            "started_at": audit.started_at.isoformat() if audit.started_at else None,
            "completed_at": audit.completed_at.isoformat()
            if audit.completed_at
            else None,
            "crawl_policy_summary": audit.crawl_policy_summary,
        },
        "pages": [
            {
                "id": p.id,
                "requested_url": p.requested_url,
                "final_url": p.final_url,
                "http_status": p.http_status,
                "title": p.title,
                "meta_description": p.meta_description,
                "word_count": p.word_count,
                "internal_link_count": p.internal_link_count,
                "external_link_count": p.external_link_count,
                "response_time_ms": p.response_time_ms,
                "response_size_bytes": p.response_size_bytes,
                "crawl_depth": p.crawl_depth,
                "indexability_status": p.indexability_status,
            }
            for p in pages
        ],
        "issues": [
            {
                "id": i.id,
                "issue_code": i.issue_code,
                "title": i.title,
                "category": i.category,
                "severity": i.severity,
                "priority_score": i.priority_score,
                "impact": i.impact,
                "confidence": i.confidence,
                "estimated_effort": i.estimated_effort,
                "status": i.status,
                "affected_page_count": i.affected_page_count,
                "description": i.description,
                "suggested_fix": i.suggested_fix,
                "example_fix": i.example_fix,
                "priority_reason": i.priority_reason,
                "evidences": [
                    {
                        "page_url": e.page_url,
                        "observed_value": e.observed_value,
                        "expected_value": e.expected_value,
                        "evidence_snippet": e.evidence_snippet,
                        "explanation": e.explanation,
                    }
                    for e in (i.evidences or [])
                ],
            }
            for i in issues
        ],
    }
