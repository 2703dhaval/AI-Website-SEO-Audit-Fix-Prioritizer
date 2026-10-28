from collections import defaultdict
from typing import Any

from app.seo_checks.base import CheckResult, IssueFindingEvidence


def check_internal_links(crawled_pages: list[dict[str, Any]]) -> list[CheckResult]:
    results = []

    # Map of page URL -> crawled page dict
    pages_by_url = {p["final_url"]: p for p in crawled_pages}
    # Track incoming internal links per target URL
    incoming_links_count = defaultdict(int)
    incoming_links_sources = defaultdict(list)

    # 1. Broken Internal Links & Links to Redirects & Empty Anchor Text
    broken_link_evidences = []
    redirect_link_evidences = []
    empty_anchor_evidences = []
    excessive_links_evidences = []
    deep_page_evidences = []

    for p in crawled_pages:
        source_url = p["final_url"]
        internal_links = p.get("internal_links", [])

        # Check total internal link count
        if len(internal_links) > 150:
            excessive_links_evidences.append(
                IssueFindingEvidence(
                    page_url=source_url,
                    observed_value=f"{len(internal_links)} internal links",
                    expected_value="Under 150 internal links per page for focused link equity",
                    evidence_snippet=f"Page contains {len(internal_links)} internal <a> anchors",
                    evidence_type="internal_links_count",
                    explanation="High internal link volume dilutes PageRank distribution across linked targets.",
                )
            )

        # Check crawl depth
        if p.get("crawl_depth", 0) > 3:
            deep_page_evidences.append(
                IssueFindingEvidence(
                    page_url=source_url,
                    observed_value=f"Crawl depth: {p.get('crawl_depth')}",
                    expected_value="Depth <= 3 clicks from homepage",
                    evidence_snippet=f"Depth {p.get('crawl_depth')} hops away from seed URL",
                    evidence_type="crawl_depth",
                    explanation="Page is buried deeply in the site architecture and receives less crawler attention.",
                )
            )

        for link in internal_links:
            target_url = link.get("href", "")
            anchor_text = link.get("text", "").strip()

            incoming_links_count[target_url] += 1
            incoming_links_sources[target_url].append(source_url)

            # Check empty anchor text
            if not anchor_text and not link.get("has_image_alt"):
                empty_anchor_evidences.append(
                    IssueFindingEvidence(
                        page_url=source_url,
                        observed_value="Link with missing or blank anchor text",
                        expected_value="Descriptive anchor text describing destination",
                        evidence_snippet=f'<a href="{target_url}"></a>',
                        evidence_type="anchor_text",
                        explanation=f"Link to {target_url} has no visible anchor text or image alt text.",
                    )
                )

            # If target page was also crawled, check its HTTP status
            target_page = pages_by_url.get(target_url)
            if target_page:
                status = target_page.get("http_status", 200)
                if status >= 400:
                    broken_link_evidences.append(
                        IssueFindingEvidence(
                            page_url=source_url,
                            observed_value=f"Links to {target_url} which returned HTTP {status}",
                            expected_value="All internal links must resolve to HTTP 200 OK",
                            evidence_snippet=f"Found on {source_url} linking to {target_url} (HTTP {status})",
                            evidence_type="broken_link",
                            explanation=f"Internal link points to a non-existent or erroring page (HTTP {status}).",
                        )
                    )
                elif len(target_page.get("redirect_chain", [])) > 0:
                    redirect_link_evidences.append(
                        IssueFindingEvidence(
                            page_url=source_url,
                            observed_value=f"Links to {target_url} which redirects to {target_page.get('final_url')}",
                            expected_value="Links should target final destination directly",
                            evidence_snippet=f"Href: {target_url} -> Redirects to: {target_page.get('final_url')}",
                            evidence_type="redirect_link",
                            explanation="Internal link causes an unnecessary redirect hop instead of linking directly to final URL.",
                        )
                    )

    # Broken links check
    if broken_link_evidences:
        results.append(
            CheckResult(
                issue_code="ERR_BROKEN_INTERNAL_LINK",
                title="Broken Internal Links Detected (4xx / 5xx Destinations)",
                category="internal_linking",
                severity="critical",
                impact=0.85,
                confidence=1.0,
                estimated_effort=0.2,
                description="Internal links on the website point to URLs returning error status codes.",
                why_it_matters="Broken internal links create poor user experiences and stop search bot spiders in their tracks, preventing full site indexation.",
                suggested_fix="Update the affected href attributes to active live URLs, or remove obsolete links.",
                example_fix='Replace href="/old-url" with href="/new-live-url"',
                priority_reason="High impact on user journey and bot crawlability; very easy to fix.",
                evidences=broken_link_evidences,
            )
        )

    # Links to redirects check
    if redirect_link_evidences:
        results.append(
            CheckResult(
                issue_code="WARN_INTERNAL_LINK_TO_REDIRECT",
                title="Internal Links Pointing to Redirects",
                category="internal_linking",
                severity="medium",
                impact=0.5,
                confidence=0.95,
                estimated_effort=0.2,
                description="Internal links target URLs that redirect to another page rather than linking directly.",
                why_it_matters="Forces visitors and search bots through an extra redirect hop, adding latency and wasting crawl budget.",
                suggested_fix="Update internal link href targets directly to the destination URL.",
                example_fix='Change href="/about" to href="/about-us" if /about redirects to /about-us.',
                priority_reason="Reduces page latency and consolidates link signals.",
                evidences=redirect_link_evidences,
            )
        )

    # Empty anchor text check
    if empty_anchor_evidences:
        # Deduplicate to max 10 sample evidences
        results.append(
            CheckResult(
                issue_code="WARN_EMPTY_ANCHOR_TEXT",
                title="Internal Links with Empty or Missing Anchor Text",
                category="internal_linking",
                severity="low",
                impact=0.4,
                confidence=0.9,
                estimated_effort=0.15,
                description="Internal links have no visible anchor text or image alt text describing the link destination.",
                why_it_matters="Anchor text provides search engines and screen readers with semantic clues about the destination page context.",
                suggested_fix="Add descriptive, keyword-rich anchor text to the link tag.",
                example_fix='<a href="/pricing">View Pricing Plans</a> instead of <a href="/pricing"></a>',
                priority_reason="Improves accessibility and semantic link relevance.",
                evidences=empty_anchor_evidences[:20],
            )
        )

    # Excessive internal links check
    if excessive_links_evidences:
        results.append(
            CheckResult(
                issue_code="WARN_EXCESSIVE_INTERNAL_LINKS",
                title="Pages with Excessive Internal Links (> 150 Links)",
                category="internal_linking",
                severity="low",
                impact=0.35,
                confidence=0.85,
                estimated_effort=0.3,
                description="Page contains more than 150 internal links.",
                why_it_matters="Dilutes internal PageRank distribution and can overwhelm mobile users with excessive navigation.",
                suggested_fix="Prune low-value footer and navigation links, focusing on high-priority topical routes.",
                example_fix="Consolidate repetitive mega-menus into streamlined, contextual category links.",
                priority_reason="Improves crawl efficiency and link equity concentration.",
                evidences=excessive_links_evidences,
            )
        )

    # Deep pages check
    if deep_page_evidences:
        results.append(
            CheckResult(
                issue_code="WARN_DEEP_CRAWL_DEPTH",
                title="Excessively Deep Pages (> 3 Clicks from Homepage)",
                category="internal_linking",
                severity="medium",
                impact=0.55,
                confidence=0.9,
                estimated_effort=0.35,
                description="Important pages are buried 4 or more clicks away from the homepage.",
                why_it_matters="Pages deeper than 3 clicks receive significantly less internal PageRank and are crawled less frequently by search bots.",
                suggested_fix="Add contextual internal links from higher-level category pages or the homepage to flatten site architecture.",
                example_fix="Feature important deep articles or product pages in category hubs or sidebar highlights.",
                priority_reason="Elevates important content closer to high-authority root pages.",
                evidences=deep_page_evidences,
            )
        )

    # Potential orphan pages check (qualified to available dataset)
    orphan_evidences = []
    # Only consider pages crawled with depth > 0 (homepage has depth 0 so naturally has 0 incoming within crawl)
    for p in crawled_pages:
        url = p["final_url"]
        if p.get("crawl_depth", 0) > 0 and incoming_links_count[url] == 0:
            orphan_evidences.append(
                IssueFindingEvidence(
                    page_url=url,
                    observed_value="0 incoming internal links from within crawled dataset",
                    expected_value="At least 1-2 incoming contextual internal links",
                    evidence_snippet=f"Discovered via initial queue or sitemap, but no crawled page links to {url}",
                    evidence_type="internal_links_count",
                    explanation="Page has no incoming links within the current crawl scope. It may be an orphan page.",
                )
            )
    if orphan_evidences:
        results.append(
            CheckResult(
                issue_code="WARN_POTENTIAL_ORPHAN_PAGE",
                title="Potential Orphan Pages Within Crawled Dataset",
                category="internal_linking",
                severity="medium",
                impact=0.6,
                confidence=0.7,
                estimated_effort=0.25,
                description="Pages in the crawled dataset have no internal incoming links from other audited pages.",
                why_it_matters="Orphan pages cannot be discovered by search bots traversing standard links and receive 0 internal link equity.",
                suggested_fix="Link to these pages from relevant parent pages or site navigation menus.",
                example_fix="Add link to page in related blog posts or main navigation.",
                priority_reason="Brings disconnected pages back into the indexable link architecture.",
                evidences=orphan_evidences,
            )
        )

    return results
