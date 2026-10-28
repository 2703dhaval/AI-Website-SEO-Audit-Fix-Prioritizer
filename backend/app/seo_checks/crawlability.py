from typing import Any

from app.seo_checks.base import CheckResult, IssueFindingEvidence


def check_crawlability(
    crawled_pages: list[dict[str, Any]], robots_summary: dict[str, Any]
) -> list[CheckResult]:
    results = []

    # 1. 4xx Client Errors
    evidences_4xx = []
    for p in crawled_pages:
        status = p.get("http_status", 200)
        if 400 <= status < 500:
            evidences_4xx.append(
                IssueFindingEvidence(
                    page_url=p["final_url"],
                    observed_value=f"HTTP Status {status}",
                    expected_value="HTTP Status 200 OK",
                    evidence_snippet=f"Requested: {p['requested_url']} -> Status: {status}",
                    evidence_type="http_status",
                    explanation=f"Page returned client error status {status}. Search crawlers and users cannot access this page content.",
                )
            )
    if evidences_4xx:
        results.append(
            CheckResult(
                issue_code="ERR_HTTP_4XX",
                title="Broken Pages Returning 4xx Client Errors",
                category="crawlability",
                severity="critical",
                impact=0.9,
                confidence=1.0,
                estimated_effort=0.3,
                description="Pages returned 4xx HTTP status codes indicating they are missing, deleted, or forbidden.",
                why_it_matters="4xx errors waste search crawler budget, cause immediate bounce rates for visitors, and break link equity flow across your site.",
                suggested_fix="Restore deleted pages, update incoming links to active URLs, or configure clean 301 redirects to the most relevant live page.",
                example_fix="Rewrite rule: Redirect 301 /old-page /new-page",
                priority_reason="Broken URLs disrupt user journeys and cause search engines to de-index pages quickly.",
                evidences=evidences_4xx,
            )
        )

    # 2. 5xx Server Errors
    evidences_5xx = []
    for p in crawled_pages:
        status = p.get("http_status", 200)
        if 500 <= status < 600:
            evidences_5xx.append(
                IssueFindingEvidence(
                    page_url=p["final_url"],
                    observed_value=f"HTTP Status {status}",
                    expected_value="HTTP Status 200 OK",
                    evidence_snippet=f"URL: {p['requested_url']} -> Server error {status}",
                    evidence_type="http_status",
                    explanation=f"Web server failed to respond properly (Status {status}).",
                )
            )
    if evidences_5xx:
        results.append(
            CheckResult(
                issue_code="ERR_HTTP_5XX",
                title="Critical Server Errors (5xx)",
                category="crawlability",
                severity="critical",
                impact=0.95,
                confidence=1.0,
                estimated_effort=0.6,
                description="Web server threw internal errors when responding to page requests.",
                why_it_matters="5xx server errors indicate server unreliability. Search engines like Google drop crawl rate dramatically when encountering server failures.",
                suggested_fix="Inspect web server and application backend logs to resolve unhandled exceptions, database timeouts, or web server misconfigurations.",
                example_fix="Check application logs, resolve runtime exceptions, or increase timeout thresholds.",
                priority_reason="Server crashes prevent crawling, indexing, and all user transactions.",
                evidences=evidences_5xx,
            )
        )

    # 3. Redirect Chains
    evidences_chains = []
    for p in crawled_pages:
        chain = p.get("redirect_chain", [])
        if len(chain) > 1:
            evidences_chains.append(
                IssueFindingEvidence(
                    page_url=p["final_url"],
                    observed_value=f"{len(chain)} redirect hops: {' -> '.join(chain)}",
                    expected_value="Direct link (0 redirects) or maximum 1 single 301 redirect hop",
                    evidence_snippet=" -> ".join(chain),
                    evidence_type="redirect_chain",
                    explanation=f"Page required {len(chain)} hops to resolve to destination {p['final_url']}.",
                )
            )
    if evidences_chains:
        results.append(
            CheckResult(
                issue_code="WARN_REDIRECT_CHAIN",
                title="Inefficient Redirect Chains",
                category="crawlability",
                severity="medium",
                impact=0.6,
                confidence=0.95,
                estimated_effort=0.3,
                description="Multiple successive redirects occur before landing on the final page.",
                why_it_matters="Redirect chains slow down page load times, waste crawl quota, and risk search engines abandoning the crawl before indexing.",
                suggested_fix="Update all internal links and redirect rules to point directly to the final destination URL.",
                example_fix="Change link pointing to /url-a directly to /url-c instead of /url-a -> /url-b -> /url-c",
                priority_reason="Chains introduce cumulative latency and degrade mobile crawl performance.",
                evidences=evidences_chains,
            )
        )

    # 4. Pages with Noindex Directive
    evidences_noindex = []
    for p in crawled_pages:
        directives = (p.get("robots_directives") or "").lower()
        if "noindex" in directives:
            evidences_noindex.append(
                IssueFindingEvidence(
                    page_url=p["final_url"],
                    observed_value=f"Directives: {directives}",
                    expected_value="Indexable (no noindex directive) unless intentionally hidden",
                    evidence_snippet=f'<meta name="robots" content="{directives}">',
                    evidence_type="meta_tag",
                    explanation="Page contains 'noindex' directive instructing search engines not to show this page in search results.",
                )
            )
    if evidences_noindex:
        results.append(
            CheckResult(
                issue_code="INFO_PAGE_NOINDEX",
                title="Pages Marked as Noindex",
                category="crawlability",
                severity="low",
                impact=0.4,
                confidence=1.0,
                estimated_effort=0.2,
                description="Pages contain noindex meta tags or X-Robots-Tag headers.",
                why_it_matters="If these pages are meant to rank and drive organic traffic, the noindex directive completely excludes them from Google search results.",
                suggested_fix="Review these URLs. If intentional (e.g. thank-you pages, admin areas), no action needed. If unintended, remove the noindex directive.",
                example_fix='Change: <meta name="robots" content="noindex"> to <meta name="robots" content="index, follow">',
                priority_reason="Critical if accidental; informational if deliberate.",
                evidences=evidences_noindex,
            )
        )

    # 5. Missing or Inaccessible robots.txt
    if (
        not robots_summary.get("fetched_successfully", False)
        and robots_summary.get("status_code") != 404
    ):
        results.append(
            CheckResult(
                issue_code="WARN_ROBOTS_TXT_INACCESSIBLE",
                title="Robots.txt File Missing or Inaccessible",
                category="crawlability",
                severity="medium",
                impact=0.5,
                confidence=0.9,
                estimated_effort=0.2,
                description="The crawler could not retrieve robots.txt from the website root.",
                why_it_matters="While a missing robots.txt defaults to allowing crawls, an inaccessible or erroring robots.txt (e.g. 5xx or 403) can pause Googlebot crawling completely.",
                suggested_fix="Provide a valid, accessible robots.txt at /robots.txt with appropriate crawl directives and sitemap declarations.",
                example_fix="User-agent: *\nAllow: /\nSitemap: https://example.com/sitemap.xml",
                priority_reason="Ensures search engine bots have clear guidance on permitted sections.",
                evidences=[
                    IssueFindingEvidence(
                        page_url=robots_summary.get("robots_url", "/robots.txt"),
                        observed_value=f"Status: {robots_summary.get('status_code', 'Error')}",
                        expected_value="HTTP 200 with valid directives",
                        evidence_snippet=robots_summary.get("summary", ""),
                        evidence_type="robots_txt",
                        explanation="Failed to cleanly access robots.txt file.",
                    )
                ],
            )
        )

    # 6. Mixed Content: Insecure HTTP links on HTTPS pages
    evidences_mixed = []
    for p in crawled_pages:
        url = p.get("final_url", "")
        if url.startswith("https://"):
            insecure_links = [
                l["href"]
                for l in p.get("internal_links", [])
                if l.get("href", "").startswith("http://")
            ]
            if insecure_links:
                evidences_mixed.append(
                    IssueFindingEvidence(
                        page_url=url,
                        observed_value=f"{len(insecure_links)} insecure HTTP internal links found",
                        expected_value="All internal links must use HTTPS",
                        evidence_snippet=", ".join(insecure_links[:3]),
                        evidence_type="internal_link",
                        explanation=f"Page is served via secure HTTPS but contains {len(insecure_links)} internal links targeting insecure HTTP.",
                    )
                )
    if evidences_mixed:
        results.append(
            CheckResult(
                issue_code="WARN_MIXED_HTTP_LINKS",
                title="Insecure HTTP Internal Links on Secure HTTPS Pages",
                category="crawlability",
                severity="medium",
                impact=0.55,
                confidence=1.0,
                estimated_effort=0.2,
                description="HTTPS pages link internally to http:// URLs.",
                why_it_matters="Triggers unnecessary redirects, degrades user security confidence, and can prompt browser security warnings.",
                suggested_fix="Update all internal links to use https:// URLs or root-relative paths.",
                example_fix='Change href="http://example.com/page" to href="https://example.com/page" or href="/page"',
                priority_reason="Simple fix that eliminates redirect delays and secures user navigation.",
                evidences=evidences_mixed,
            )
        )

    return results
