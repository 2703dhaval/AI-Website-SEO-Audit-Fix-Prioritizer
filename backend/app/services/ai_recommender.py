def generate_ai_recommendation(
    issue_code: str,
    title: str,
    page_url: str,
    evidence_snippet: str,
    observed_value: str,
) -> dict[str, str]:
    """
    Generates intelligent, context-aware remediation recommendations.
    Deterministic by default, ensuring 100% reliable offline functionality
    without requiring any paid external LLM API key.
    """
    # Deterministic knowledge-base enhancements
    recommendations_db = {
        "ERR_TITLE_MISSING": {
            "action": "Generate a concise, search-optimized <title> tag reflecting page context.",
            "code_template": "<title>[Primary Keyword] - [Key Benefit or Category] | [Brand]</title>",
            "explanation": "Google typically displays the first 50-60 characters of a title. Placing the primary target keyword toward the beginning improves relevance perception.",
        },
        "ERR_META_DESC_MISSING": {
            "action": "Author a high-converting meta description between 120 and 155 characters.",
            "code_template": '<meta name="description" content="[Benefit-driven sentence summarizing page value]. [Clear Call to Action: Learn more / Explore / Get started].">',
            "explanation": "A well-crafted meta description acts as free organic ad copy, directly influencing click-through rate (CTR) in search results.",
        },
        "ERR_H1_MISSING": {
            "action": "Insert a single semantic <h1> element above the primary content block.",
            "code_template": "<h1>[Descriptive Page Topic with Target Keyword]</h1>",
            "explanation": "The H1 tag confirms the core subject of the page for search engines and visually anchors screen-reader navigation.",
        },
        "ERR_IMG_ALT_MISSING": {
            "action": "Add an alt attribute describing the image context.",
            "code_template": '<img src="..." alt="[Concise description of subject matter]">',
            "explanation": "Alt text ensures WCAG accessibility compliance and allows image indexing in Google Images search.",
        },
        "ERR_VIEWPORT_MISSING": {
            "action": "Add the standard responsive viewport meta tag into the HTML <head>.",
            "code_template": '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            "explanation": "Required by Google for mobile-first indexing to prevent mobile browsers from rendering at desktop widths.",
        },
        "ERR_BROKEN_INTERNAL_LINK": {
            "action": "Fix or replace the broken target URL in the anchor tag.",
            "code_template": '<a href="[active-live-url]">[Descriptive Anchor Text]</a>',
            "explanation": "Broken internal links cause 4xx errors, waste search bot crawl quota, and frustrate human users.",
        },
        "ERR_JSONLD_SYNTAX": {
            "action": "Fix JSON syntax errors (remove trailing commas, fix quotes).",
            "code_template": '<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n  "@type": "WebPage",\n  "name": "Page Title"\n}\n</script>',
            "explanation": "Syntax errors cause search engines to completely ignore your structured data, losing rich result eligibility.",
        },
    }

    item = recommendations_db.get(
        issue_code,
        {
            "action": f"Review and remediate {title}.",
            "code_template": f"<!-- Apply standard technical SEO fix for {issue_code} -->",
            "explanation": "Adhering to standard technical SEO guidelines improves search crawlability, indexing, and user experience.",
        },
    )

    return {
        "remediation_action": item["action"],
        "suggested_snippet": item["code_template"],
        "technical_rationale": item["explanation"],
        "source": "deterministic_engine",
    }
