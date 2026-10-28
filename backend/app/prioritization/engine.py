import math


def calculate_scope(affected_count: int, total_pages: int) -> float:
    """
    Calculates normalized scope [0.0, 1.0] using a bounded logarithmic curve
    relative to the total crawled pages.
    """
    if affected_count <= 0:
        return 0.0
    total = max(total_pages, 1)
    # Logarithmic scaling gives meaningful weight to single occurrences on small sites
    # while preventing massive site crawls from skewing disproportionately.
    raw_scope = math.log1p(affected_count) / math.log1p(total)
    return round(min(1.0, max(0.1, raw_scope)), 3)


def calculate_priority_score(
    impact: float, scope: float, confidence: float, effort: float
) -> float:
    """
    Deterministic fix prioritization formula:
    Priority Score = 100 * (0.45 * Impact + 0.30 * Scope + 0.25 * Confidence) * (1 - 0.15 * Effort)
    All inputs normalized between 0.0 and 1.0.
    Output is bounded between 0.0 and 100.0.
    """
    # Clamp inputs
    imp = min(1.0, max(0.0, impact))
    sc = min(1.0, max(0.0, scope))
    conf = min(1.0, max(0.0, confidence))
    eff = min(1.0, max(0.0, effort))

    raw_score = 100.0 * (0.45 * imp + 0.30 * sc + 0.25 * conf) * (1.0 - 0.15 * eff)
    return round(min(100.0, max(0.0, raw_score)), 1)


def generate_priority_reason(
    severity: str, priority_score: float, impact: float, scope: float, effort: float
) -> str:
    """Generates an intuitive, evidence-based reason for the priority ranking."""
    effort_desc = (
        "minimal" if effort < 0.25 else ("moderate" if effort < 0.55 else "substantial")
    )
    if priority_score >= 80:
        return f"Urgent priority: High SEO consequence ({int(impact * 100)}% impact) combined with {effort_desc} implementation effort makes this an immediate quick-win."
    elif priority_score >= 60:
        return f"High priority: Significant ranking influence ({int(impact * 100)}% impact) affecting {int(scope * 100)}% of audit scope."
    elif priority_score >= 40:
        return f"Medium priority: Noticeable quality improvement ({int(impact * 100)}% impact); schedule into upcoming technical sprint."
    else:
        return "Low/Advisory priority: Recommended best practice with minor organic ranking impact."
