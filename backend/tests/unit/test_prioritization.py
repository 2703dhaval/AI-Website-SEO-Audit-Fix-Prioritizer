import pytest
from app.prioritization.engine import calculate_priority_score, calculate_scope, generate_priority_reason
from app.prioritization.health_score import calculate_seo_health_score
from app.seo_checks.base import CheckResult, IssueFindingEvidence


class TestPrioritizationEngine:
    def test_priority_score_calculation(self):
        # Formula: 100 * (0.45 * Impact + 0.30 * Scope + 0.25 * Confidence) * (1 - 0.15 * Effort)
        # Test case: Impact=1.0, Scope=1.0, Confidence=1.0, Effort=0.0 -> Score should be exactly 100.0
        score_max = calculate_priority_score(impact=1.0, scope=1.0, confidence=1.0, effort=0.0)
        assert score_max == 100.0

        # High impact (0.9), low effort (0.1), scope (0.5), conf (1.0)
        score_quickwin = calculate_priority_score(impact=0.9, scope=0.5, confidence=1.0, effort=0.1)
        assert 70.0 <= score_quickwin <= 85.0

        # Low impact (0.2), high effort (0.8)
        score_low = calculate_priority_score(impact=0.2, scope=0.2, confidence=0.8, effort=0.8)
        assert score_low < 35.0

    def test_scope_calculation_bounded(self):
        # 1 page affected out of 10
        scope_single = calculate_scope(affected_count=1, total_pages=10)
        assert 0.1 <= scope_single <= 0.4

        # All 10 pages affected out of 10
        scope_all = calculate_scope(affected_count=10, total_pages=10)
        assert scope_all == 1.0

        # Zero pages
        assert calculate_scope(0, 10) == 0.0

    def test_seo_health_score_deductions_and_cap(self):
        # Perfect audit (0 issues)
        perfect_score, breakdown = calculate_seo_health_score([], total_crawled_pages=10)
        assert perfect_score == 100.0
        assert breakdown["baseline_score"] == 100.0

        # Critical issue
        crit_issue = CheckResult(
            issue_code="ERR_HTTP_5XX",
            title="Server 500",
            category="crawlability",
            severity="critical",
            impact=0.95,
            confidence=1.0,
            estimated_effort=0.5,
            description="desc",
            why_it_matters="why",
            suggested_fix="fix",
            evidences=[IssueFindingEvidence(page_url="https://example.com/err")]
        )
        score_crit, breakdown_crit = calculate_seo_health_score([crit_issue], total_crawled_pages=5)
        assert score_crit < 90.0
        assert breakdown_crit["category_penalties"]["crawlability"] > 0
