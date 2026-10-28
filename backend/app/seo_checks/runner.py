from typing import Any

from app.seo_checks.base import CheckResult
from app.seo_checks.crawlability import check_crawlability
from app.seo_checks.duplicates import check_duplicates
from app.seo_checks.internal_links import check_internal_links
from app.seo_checks.on_page import check_on_page
from app.seo_checks.performance import check_performance
from app.seo_checks.structured_data import check_structured_data


def run_all_seo_checks(
    crawled_pages: list[dict[str, Any]], robots_summary: dict[str, Any]
) -> list[CheckResult]:
    """
    Executes all technical and on-page SEO detection modules across
    the crawled dataset and aggregates findings.
    """
    all_findings: list[CheckResult] = []

    all_findings.extend(check_crawlability(crawled_pages, robots_summary))
    all_findings.extend(check_on_page(crawled_pages))
    all_findings.extend(check_internal_links(crawled_pages))
    all_findings.extend(check_structured_data(crawled_pages))
    all_findings.extend(check_performance(crawled_pages))
    all_findings.extend(check_duplicates(crawled_pages))

    return all_findings
