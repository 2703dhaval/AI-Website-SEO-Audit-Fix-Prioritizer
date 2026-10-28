from typing import Any

from app.seo_checks.base import CheckResult

SEVERITY_BASE_DEDUCTIONS = {
    "critical": 14.0,
    "high": 8.0,
    "medium": 4.0,
    "low": 1.5,
    "informational": 0.0,
}

CATEGORY_MAX_PENALTY = {
    "crawlability": 35.0,
    "on_page": 30.0,
    "internal_linking": 20.0,
    "structured_data": 15.0,
    "performance": 15.0,
    "duplicates": 20.0,
}


def calculate_seo_health_score(
    issues: list[CheckResult], total_crawled_pages: int
) -> tuple[float, dict[str, Any]]:
    """
    Computes a transparent, deterministic SEO Health Score (0.0 to 100.0).
    Starts at 100.0 and applies bounded penalties per category based on
    issue severity and affected scope.
    """
    total_pages = max(total_crawled_pages, 1)
    category_penalties = {cat: 0.0 for cat in CATEGORY_MAX_PENALTY}
    category_issue_counts = {cat: 0 for cat in CATEGORY_MAX_PENALTY}
    deductions_detail = []

    for issue in issues:
        base_deduction = SEVERITY_BASE_DEDUCTIONS.get(issue.severity.lower(), 2.0)
        # Scope factor: scaled from 1.0 (single page) up to 1.5 (all pages affected)
        scope_ratio = issue.affected_page_count / total_pages
        scope_factor = 1.0 + (0.5 * min(1.0, scope_ratio))

        issue_penalty = base_deduction * scope_factor
        category = issue.category.lower()
        if category in category_penalties:
            category_penalties[category] += issue_penalty
            category_issue_counts[category] += 1
            deductions_detail.append(
                {
                    "issue_code": issue.issue_code,
                    "title": issue.title,
                    "severity": issue.severity,
                    "category": category,
                    "penalty": round(issue_penalty, 2),
                    "affected_pages": issue.affected_page_count,
                }
            )

    # Cap category penalties to ensure balanced category influence
    total_deduction = 0.0
    category_scores = {}
    for cat, cap in CATEGORY_MAX_PENALTY.items():
        capped_penalty = min(cap, category_penalties[cat])
        total_deduction += capped_penalty
        # Sub-score per category on 100 scale
        cat_score = max(0.0, 100.0 - (capped_penalty / cap * 100.0))
        category_scores[cat] = round(cat_score, 1)

    final_score = max(0.0, min(100.0, 100.0 - total_deduction))
    rounded_score = round(final_score, 1)

    explanation = {
        "version": "v1.0",
        "baseline_score": 100.0,
        "final_health_score": rounded_score,
        "total_deduction": round(total_deduction, 2),
        "category_scores": category_scores,
        "category_penalties": {k: round(v, 2) for k, v in category_penalties.items()},
        "deductions_breakdown": deductions_detail,
    }

    return rounded_score, explanation
