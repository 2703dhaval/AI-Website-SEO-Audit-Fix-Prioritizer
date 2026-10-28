from typing import Any

from app.seo_checks.base import CheckResult, IssueFindingEvidence


def check_performance(crawled_pages: list[dict[str, Any]]) -> list[CheckResult]:
    results = []

    slow_response_evidences = []
    large_html_evidences = []
    missing_dimensions_evidences = []

    for p in crawled_pages:
        url = p["final_url"]
        rt = p.get("response_time_ms", 0.0)
        size_bytes = p.get("response_size_bytes", 0)

        # Check slow response time (> 1200ms)
        if rt > 1200:
            slow_response_evidences.append(
                IssueFindingEvidence(
                    page_url=url,
                    observed_value=f"{rt:.1f} ms response time",
                    expected_value="Under 600 ms Time-To-First-Byte (TTFB)",
                    evidence_snippet=f"Initial HTML fetch latency: {rt:.1f}ms",
                    evidence_type="performance_metric",
                    explanation=f"Server took {rt:.1f}ms to respond with HTML, which degrades Core Web Vitals (TTFB/LCP).",
                )
            )

        # Check large HTML (> 800 KB)
        if size_bytes > 800 * 1024:
            size_kb = size_bytes / 1024
            large_html_evidences.append(
                IssueFindingEvidence(
                    page_url=url,
                    observed_value=f"{size_kb:.1f} KB HTML size",
                    expected_value="Under 250 KB uncompressed HTML document",
                    evidence_snippet=f"HTML payload size: {size_kb:.1f} KB",
                    evidence_type="performance_metric",
                    explanation="Oversized HTML documents delay DOM parsing and increase mobile bandwidth consumption.",
                )
            )

        # Images missing dimensions
        images = p.get("images", [])
        no_dim_images = [
            img["src"] for img in images if not img.get("has_dimensions", False)
        ]
        if len(no_dim_images) >= 5:
            missing_dimensions_evidences.append(
                IssueFindingEvidence(
                    page_url=url,
                    observed_value=f"{len(no_dim_images)} images without width/height dimensions",
                    expected_value="Explicit width and height on <img> elements to reserve layout space",
                    evidence_snippet=", ".join(no_dim_images[:3]),
                    evidence_type="image_dimensions",
                    explanation="Missing dimensions cause browser reflows and Cumulative Layout Shift (CLS).",
                )
            )

    if slow_response_evidences:
        results.append(
            CheckResult(
                issue_code="WARN_SLOW_RESPONSE_TIME",
                title="Slow Server Response Time (> 1.2 Seconds)",
                category="performance",
                severity="medium",
                impact=0.6,
                confidence=0.85,
                estimated_effort=0.4,
                description="Initial HTML response time exceeded 1200ms.",
                why_it_matters="Slow response times directly hurt Time To First Byte (TTFB), user conversion rates, and crawl budget allocation.",
                suggested_fix="Implement server-side caching (Redis, Varnish), enable CDN edge caching, or optimize backend database queries.",
                example_fix="Enable page caching and HTTP/2 or HTTP/3 on the origin web server.",
                priority_reason="Core Web Vitals factor with direct impact on user bounce rate.",
                evidences=slow_response_evidences,
            )
        )

    if large_html_evidences:
        results.append(
            CheckResult(
                issue_code="WARN_LARGE_HTML_PAYLOAD",
                title="Oversized HTML Document Payload (> 800 KB)",
                category="performance",
                severity="medium",
                impact=0.5,
                confidence=0.9,
                estimated_effort=0.35,
                description="Page HTML payload is excessively large.",
                why_it_matters="Heavy HTML blocks DOM parsing, slows mobile devices, and burns crawl bandwidth.",
                suggested_fix="Minify HTML, externalize embedded inline SVGs or large base64 data, and enable Gzip/Brotli compression.",
                example_fix="Enable Brotli/Gzip compression in Nginx/Cloudflare and move inline base64 images to external assets.",
                priority_reason="Reduces data transfer and accelerates browser rendering.",
                evidences=large_html_evidences,
            )
        )

    if missing_dimensions_evidences:
        results.append(
            CheckResult(
                issue_code="WARN_IMG_DIMENSIONS_MISSING",
                title="Images Missing Width and Height Attributes (CLS Risk)",
                category="performance",
                severity="low",
                impact=0.4,
                confidence=0.9,
                estimated_effort=0.25,
                description="Images do not specify explicit width and height dimensions.",
                why_it_matters="Without explicit aspect-ratio or dimensions, browsers cannot reserve space before images download, causing jarring Cumulative Layout Shift (CLS).",
                suggested_fix="Add width and height attributes or CSS aspect-ratio property to images.",
                example_fix='<img src="/hero.jpg" width="800" height="400" alt="Hero Banner">',
                priority_reason="Protects Core Web Vitals layout stability score.",
                evidences=missing_dimensions_evidences,
            )
        )

    return results
