from typing import Any

from app.seo_checks.base import CheckResult, IssueFindingEvidence


def check_structured_data(crawled_pages: list[dict[str, Any]]) -> list[CheckResult]:
    results = []

    syntax_error_evidences = []
    missing_schema_evidences = []
    malformed_schema_evidences = []

    for p in crawled_pages:
        url = p["final_url"]
        json_ld_list = p.get("json_ld_scripts", [])

        if not json_ld_list:
            # Informational check for missing structured data
            if p.get("http_status", 200) == 200:
                missing_schema_evidences.append(
                    IssueFindingEvidence(
                        page_url=url,
                        observed_value="0 JSON-LD schema blocks detected",
                        expected_value="Relevant Schema.org markup (e.g. WebSite, Organization, Article, Product)",
                        evidence_snippet="No <script type='application/ld+json'> found",
                        evidence_type="structured_data",
                        explanation="Page has no structured data markup, missing opportunities for Google Rich Snippets.",
                    )
                )
            continue

        for item in json_ld_list:
            if item.get("error"):
                syntax_error_evidences.append(
                    IssueFindingEvidence(
                        page_url=url,
                        observed_value=f"JSON Syntax Error: {item['error']}",
                        expected_value="Valid JSON-LD schema object",
                        evidence_snippet=item.get("raw", "")[:120],
                        evidence_type="structured_data",
                        explanation=f"Malformed JSON in structured data block: {item['error']}",
                    )
                )
            elif item.get("parsed"):
                parsed = item["parsed"]
                if isinstance(parsed, dict):
                    if not parsed.get("@context") or not parsed.get("@type"):
                        malformed_schema_evidences.append(
                            IssueFindingEvidence(
                                page_url=url,
                                observed_value=f"Missing @context or @type in schema: {str(parsed)[:60]}",
                                expected_value="Standard Schema.org declaration with '@context': 'https://schema.org' and '@type'",
                                evidence_snippet=item.get("raw", "")[:120],
                                evidence_type="structured_data",
                                explanation="Schema object is missing required '@context' or '@type' properties.",
                            )
                        )

    # JSON syntax error
    if syntax_error_evidences:
        results.append(
            CheckResult(
                issue_code="ERR_JSONLD_SYNTAX",
                title="Syntax Errors in JSON-LD Structured Data",
                category="structured_data",
                severity="high",
                impact=0.75,
                confidence=1.0,
                estimated_effort=0.2,
                description='The page contains invalid JSON inside a `<script type="application/ld+json">` tag.',
                why_it_matters="Search engines reject invalid JSON-LD completely, voiding rich snippet eligibility (stars, FAQs, pricing, breadcrumbs).",
                suggested_fix="Validate JSON markup with a linter and fix trailing commas, unescaped quotes, or mismatched braces.",
                example_fix='{\n  "@context": "https://schema.org",\n  "@type": "Organization",\n  "name": "Scalezix"\n}',
                priority_reason="Completely invalidates rich search results.",
                evidences=syntax_error_evidences,
            )
        )

    # Malformed schema
    if malformed_schema_evidences:
        results.append(
            CheckResult(
                issue_code="WARN_SCHEMA_MALFORMED",
                title="Malformed Structured Data Object (Missing @context or @type)",
                category="structured_data",
                severity="medium",
                impact=0.55,
                confidence=0.95,
                estimated_effort=0.2,
                description="JSON-LD object lacks required Schema.org `@context` or `@type` declarations.",
                why_it_matters="Search engines cannot classify the entity type without valid schema context.",
                suggested_fix="Add `@context`: 'https://schema.org' and declare the entity `@type` (e.g. WebSite, Organization, Article).",
                example_fix='"@context": "https://schema.org", "@type": "WebPage"',
                priority_reason="Easy fix to enable valid rich search features.",
                evidences=malformed_schema_evidences,
            )
        )

    # Missing structured data
    if missing_schema_evidences:
        results.append(
            CheckResult(
                issue_code="INFO_STRUCTURED_DATA_MISSING",
                title="No JSON-LD Structured Data Detected",
                category="structured_data",
                severity="informational",
                impact=0.4,
                confidence=0.9,
                estimated_effort=0.3,
                description="Page does not include JSON-LD schema markup.",
                why_it_matters="Structured data helps search engines understand page entities and unlocks rich snippets in search results.",
                suggested_fix="Add Schema.org JSON-LD markup appropriate for the page type (e.g., Organization on homepage, Article on blog, Product on store).",
                example_fix='<script type="application/ld+json">{"@context": "https://schema.org", "@type": "WebPage", "name": "Audit"}</script>',
                priority_reason="Optional enhancement for rich result eligibility.",
                evidences=missing_schema_evidences[:15],
            )
        )

    return results
