from typing import Any

from app.seo_checks.base import CheckResult, IssueFindingEvidence


def check_on_page(crawled_pages: list[dict[str, Any]]) -> list[CheckResult]:
    results = []

    # 1. Missing Title Tag
    evidences_missing_title = []
    for p in crawled_pages:
        title = (p.get("title") or "").strip()
        if not title:
            evidences_missing_title.append(
                IssueFindingEvidence(
                    page_url=p["final_url"],
                    observed_value="No <title> tag found or title is blank",
                    expected_value="Descriptive <title> tag between 30 and 60 characters",
                    evidence_snippet="<head></head>",
                    evidence_type="title_tag",
                    explanation="The page lacks a title tag, which is the single most fundamental on-page SEO ranking signal.",
                )
            )
    if evidences_missing_title:
        results.append(
            CheckResult(
                issue_code="ERR_TITLE_MISSING",
                title="Missing or Empty Page Title Tag",
                category="on_page",
                severity="critical",
                impact=0.95,
                confidence=1.0,
                estimated_effort=0.1,
                description="The page HTML does not have a `<title>` tag or the title element is completely blank.",
                why_it_matters="The title tag is the primary anchor used by search engines to understand page topic and is displayed as the headline in search engine results pages (SERPs).",
                suggested_fix="Add a unique, relevant <title> tag summarizing the specific topic of the page, ideally 30-60 characters.",
                example_fix="<title>Primary Keyword - Secondary Benefit | Brand Name</title>",
                priority_reason="Extremely high SEO ranking impact with very low implementation effort.",
                evidences=evidences_missing_title,
            )
        )

    # 2. Title Length Heuristic (Too Short or Too Long)
    evidences_title_length = []
    for p in crawled_pages:
        title = (p.get("title") or "").strip()
        if title:
            length = len(title)
            if length < 30:
                evidences_title_length.append(
                    IssueFindingEvidence(
                        page_url=p["final_url"],
                        observed_value=f"Title length: {length} chars ('{title}')",
                        expected_value="30 to 60 characters",
                        evidence_snippet=f"<title>{title}</title>",
                        evidence_type="title_tag",
                        explanation=f"Title is too short ({length} characters). It likely misses descriptive keyword context.",
                    )
                )
            elif length > 60:
                evidences_title_length.append(
                    IssueFindingEvidence(
                        page_url=p["final_url"],
                        observed_value=f"Title length: {length} chars ('{title}')",
                        expected_value="30 to 60 characters",
                        evidence_snippet=f"<title>{title}</title>",
                        evidence_type="title_tag",
                        explanation=f"Title is too long ({length} characters) and will likely get truncated in Google desktop and mobile SERPs.",
                    )
                )
    if evidences_title_length:
        results.append(
            CheckResult(
                issue_code="WARN_TITLE_LENGTH",
                title="Title Tag Length Outside Optimal Range (30-60 Characters)",
                category="on_page",
                severity="medium",
                impact=0.5,
                confidence=0.85,
                estimated_effort=0.15,
                description="Titles shorter than 30 characters or longer than 60 characters may suffer poor click-through rates or truncation.",
                why_it_matters="Overly long titles are truncated with ellipses in search results. Overly short titles fail to communicate keyword context and user value proposition.",
                suggested_fix="Adjust titles to fit between 30 and 60 characters (approximately 500-600 pixels width) with prominent keywords near the beginning.",
                example_fix="<title>Web Development Services & Custom Software | Acme Corp</title>",
                priority_reason="Easy on-page fix that directly enhances search snippet CTR.",
                evidences=evidences_title_length,
            )
        )

    # 3. Missing Meta Description
    evidences_missing_meta = []
    for p in crawled_pages:
        desc = (p.get("meta_description") or "").strip()
        if not desc:
            evidences_missing_meta.append(
                IssueFindingEvidence(
                    page_url=p["final_url"],
                    observed_value="Missing meta description tag",
                    expected_value="Concise meta description between 70 and 160 characters",
                    evidence_snippet='<meta name="description" content="..."> is absent',
                    evidence_type="meta_description",
                    explanation="No meta description found. Search engines will pull arbitrary text snippets from page content.",
                )
            )
    if evidences_missing_meta:
        results.append(
            CheckResult(
                issue_code="ERR_META_DESC_MISSING",
                title="Missing Meta Description Tag",
                category="on_page",
                severity="high",
                impact=0.75,
                confidence=1.0,
                estimated_effort=0.15,
                description='The page lacks a `<meta name="description">` tag.',
                why_it_matters="A compelling meta description serves as organic ad copy in search results, driving organic click-through rate (CTR).",
                suggested_fix="Add an engaging meta description between 70 and 160 characters summarizing the page and including a clear call to action.",
                example_fix='<meta name="description" content="Discover professional technical SEO audits and automated fix prioritization with SEO Audit Pro. Start optimizing your website today.">',
                priority_reason="Strong impact on organic click-through rate with low technical overhead.",
                evidences=evidences_missing_meta,
            )
        )

    # 4. Meta Description Length
    evidences_desc_length = []
    for p in crawled_pages:
        desc = (p.get("meta_description") or "").strip()
        if desc:
            length = len(desc)
            if length < 70 or length > 160:
                evidences_desc_length.append(
                    IssueFindingEvidence(
                        page_url=p["final_url"],
                        observed_value=f"Meta description length: {length} chars",
                        expected_value="70 to 160 characters",
                        evidence_snippet=f'<meta name="description" content="{desc[:80]}...">',
                        evidence_type="meta_description",
                        explanation=f"Meta description has {length} characters. Optimal length is between 70 and 160 characters to avoid SERP truncation or thin preview text.",
                    )
                )
    if evidences_desc_length:
        results.append(
            CheckResult(
                issue_code="WARN_META_DESC_LENGTH",
                title="Meta Description Length Outside Recommended 70-160 Chars",
                category="on_page",
                severity="low",
                impact=0.35,
                confidence=0.8,
                estimated_effort=0.15,
                description="Meta description length is either too short (<70 characters) or too long (>160 characters).",
                why_it_matters="Search engines truncate descriptions exceeding ~160 characters. Descriptions under 70 characters often fail to offer enough detail to compel clicks.",
                suggested_fix="Revise meta descriptions to be concise, persuasive, and between 70 and 160 characters.",
                example_fix='<meta name="description" content="Explore our complete guide to SEO auditing, crawler security, and on-page optimization. Learn how to rank higher on Google today.">',
                priority_reason="Improves SERP presentation quality.",
                evidences=evidences_desc_length,
            )
        )

    # 5. Missing H1 Heading
    evidences_missing_h1 = []
    evidences_multiple_h1 = []
    for p in crawled_pages:
        h1_list = p.get("h1_list", [])
        if not h1_list:
            evidences_missing_h1.append(
                IssueFindingEvidence(
                    page_url=p["final_url"],
                    observed_value="0 <h1> tags found",
                    expected_value="Exactly 1 clear <h1> heading describing page topic",
                    evidence_snippet="<body>...no h1 found...</body>",
                    evidence_type="heading",
                    explanation="Page contains no primary <h1> heading tag.",
                )
            )
        elif len(h1_list) > 1:
            evidences_multiple_h1.append(
                IssueFindingEvidence(
                    page_url=p["final_url"],
                    observed_value=f"{len(h1_list)} <h1> tags found: {', '.join(h1_list[:2])}",
                    expected_value="Single primary <h1> heading",
                    evidence_snippet="; ".join([f"<h1>{h}</h1>" for h in h1_list[:3]]),
                    evidence_type="heading",
                    explanation=f"Page uses {len(h1_list)} <h1> elements. While modern HTML allows this, a single primary H1 provides clearer structural hierarchy.",
                )
            )
    if evidences_missing_h1:
        results.append(
            CheckResult(
                issue_code="ERR_H1_MISSING",
                title="Missing Primary H1 Heading Tag",
                category="on_page",
                severity="high",
                impact=0.7,
                confidence=1.0,
                estimated_effort=0.1,
                description="No `<h1>` heading tag was detected on the page.",
                why_it_matters="Search engines utilize the H1 heading to confirm page theme and relevance. It also anchors accessibility for screen reader navigation.",
                suggested_fix="Add a descriptive <h1> heading at the top of the main page content.",
                example_fix="<h1>AI-Powered SEO Auditing Platform</h1>",
                priority_reason="High on-page structural signal that is fast to correct.",
                evidences=evidences_missing_h1,
            )
        )
    if evidences_multiple_h1:
        results.append(
            CheckResult(
                issue_code="INFO_H1_MULTIPLE",
                title="Multiple H1 Headings Detected (Review Recommendation)",
                category="on_page",
                severity="informational",
                impact=0.25,
                confidence=0.75,
                estimated_effort=0.2,
                description="Page contains more than one `<h1>` element.",
                why_it_matters="While HTML5 supports multiple H1s (e.g. in distinct section elements), SEO best practices recommend reserving H1 for the page title and using H2-H4 for subsections.",
                suggested_fix="Consolidate subsidiary H1 elements into H2 or H3 tags to maintain a clear semantic hierarchy.",
                example_fix="Change secondary <h1> headings into <h2> sections.",
                priority_reason="Semantic improvement for accessibility and structure.",
                evidences=evidences_multiple_h1,
            )
        )

    # 6. Heading Hierarchy Irregularities (e.g., Skipping from H1 to H3 or H4)
    evidences_heading_order = []
    for p in crawled_pages:
        headings = p.get("headings", [])
        if headings:
            prev_level = 0
            has_irregularity = False
            first_skip = ""
            for h in headings:
                tag = h.get("tag", "")
                if tag.startswith("h") and len(tag) == 2 and tag[1].isdigit():
                    level = int(tag[1])
                    if prev_level > 0 and level > prev_level + 1:
                        has_irregularity = True
                        first_skip = f"H{prev_level} directly followed by H{level} ('{h.get('text', '')[:30]}')"
                        break
                    prev_level = level
            if has_irregularity:
                evidences_heading_order.append(
                    IssueFindingEvidence(
                        page_url=p["final_url"],
                        observed_value=first_skip,
                        expected_value="Sequential heading order (H1 -> H2 -> H3)",
                        evidence_snippet=first_skip,
                        evidence_type="heading",
                        explanation="Heading levels skip hierarchical steps, causing potential accessibility navigation issues.",
                    )
                )
    if evidences_heading_order:
        results.append(
            CheckResult(
                issue_code="WARN_HEADING_HIERARCHY",
                title="Irregular Heading Level Hierarchy (Skipped Heading Levels)",
                category="on_page",
                severity="low",
                impact=0.3,
                confidence=0.85,
                estimated_effort=0.2,
                description="Heading levels skip steps in the semantic hierarchy (e.g., jumping from H1 directly to H3 or H4).",
                why_it_matters="Logical heading structure enables screen readers and search bots to understand the relationship between parent and child content blocks.",
                suggested_fix="Structure headings hierarchically without skipping levels (H1 followed by H2, then H3 subsections).",
                example_fix="Change skipped <h3> tag to <h2>.",
                priority_reason="Accessibility enhancement and semantic cleanliness.",
                evidences=evidences_heading_order,
            )
        )

    # 7. Images Missing Alt Attribute
    evidences_missing_alt = []
    for p in crawled_pages:
        images = p.get("images", [])
        missing_images = [img["src"] for img in images if not img.get("has_alt", False)]
        if missing_images:
            evidences_missing_alt.append(
                IssueFindingEvidence(
                    page_url=p["final_url"],
                    observed_value=f"{len(missing_images)} images without alt attributes",
                    expected_value="Every <img> must have an alt attribute describing image content or alt='' if purely decorative",
                    evidence_snippet=", ".join(missing_images[:3]),
                    evidence_type="image",
                    explanation=f"{len(missing_images)} image(s) on this page lack the alt attribute entirely.",
                )
            )
    if evidences_missing_alt:
        results.append(
            CheckResult(
                issue_code="ERR_IMG_ALT_MISSING",
                title="Images Missing Alt Attribute",
                category="on_page",
                severity="medium",
                impact=0.6,
                confidence=1.0,
                estimated_effort=0.25,
                description="Image elements are missing the `alt` attribute.",
                why_it_matters="Alt text is required for WCAG web accessibility standards, powers Google Image search indexing, and provides fallback context when images fail to load.",
                suggested_fix="Add descriptive alt attributes for informative images, or alt='' role='presentation' for decorative graphics.",
                example_fix='<img src="/logo.png" alt="Company Logo - SEO Software">',
                priority_reason="Universal accessibility requirement and image SEO ranking factor.",
                evidences=evidences_missing_alt,
            )
        )

    # 8. Missing Viewport Meta Tag (Mobile Responsiveness)
    evidences_missing_viewport = []
    for p in crawled_pages:
        viewport = (p.get("viewport") or "").strip()
        if not viewport:
            evidences_missing_viewport.append(
                IssueFindingEvidence(
                    page_url=p["final_url"],
                    observed_value="Missing <meta name='viewport'>",
                    expected_value="<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
                    evidence_snippet="<head></head>",
                    evidence_type="meta_tag",
                    explanation="Page lacks viewport configuration, causing mobile browsers to render the page in desktop emulation mode.",
                )
            )
    if evidences_missing_viewport:
        results.append(
            CheckResult(
                issue_code="ERR_VIEWPORT_MISSING",
                title="Missing Viewport Meta Tag for Mobile Friendliness",
                category="on_page",
                severity="critical",
                impact=0.85,
                confidence=1.0,
                estimated_effort=0.05,
                description='The page lacks a `<meta name="viewport">` configuration tag.',
                why_it_matters="Google utilizes mobile-first indexing. Pages without a responsive viewport fail mobile-friendliness audits and are penalized in mobile search rankings.",
                suggested_fix="Include standard responsive viewport meta tag in the HTML `<head>`.",
                example_fix='<meta name="viewport" content="width=device-width, initial-scale=1.0">',
                priority_reason="Mobile-first indexing requirement with trivial one-line fix.",
                evidences=evidences_missing_viewport,
            )
        )

    # 9. Missing HTML Lang Declaration
    evidences_missing_lang = []
    for p in crawled_pages:
        lang = (p.get("language") or "").strip()
        if not lang:
            evidences_missing_lang.append(
                IssueFindingEvidence(
                    page_url=p["final_url"],
                    observed_value="<html> tag lacks lang attribute",
                    expected_value="<html lang='en'>",
                    evidence_snippet="<html>",
                    evidence_type="html_tag",
                    explanation="Page does not declare its primary language code.",
                )
            )
    if evidences_missing_lang:
        results.append(
            CheckResult(
                issue_code="WARN_LANG_MISSING",
                title="Missing Language Declaration on HTML Element",
                category="on_page",
                severity="low",
                impact=0.3,
                confidence=1.0,
                estimated_effort=0.05,
                description="The `<html>` element does not declare a `lang` attribute.",
                why_it_matters="The lang attribute aids search engines in geographic targeting and allows screen readers to switch pronunciation models appropriately.",
                suggested_fix="Add the appropriate ISO language code (e.g. lang='en') to the `<html>` root element.",
                example_fix='<html lang="en">',
                priority_reason="Quick accessibility and internationalization standard.",
                evidences=evidences_missing_lang,
            )
        )

    # 10. Low Word Count / Thin Content Heuristic (< 250 words)
    evidences_thin_content = []
    for p in crawled_pages:
        wc = p.get("word_count", 0)
        # Skip error pages
        if p.get("http_status", 200) == 200 and wc < 250:
            evidences_thin_content.append(
                IssueFindingEvidence(
                    page_url=p["final_url"],
                    observed_value=f"Word count: {wc} words",
                    expected_value="Meaningful body content (> 250 words for standard informational pages)",
                    evidence_snippet=f"Extracted {wc} words of visible text",
                    evidence_type="text_content",
                    explanation="Page contains minimal textual content, which may trigger low-quality or thin content signals.",
                )
            )
    if evidences_thin_content:
        results.append(
            CheckResult(
                issue_code="WARN_THIN_CONTENT",
                title="Thin Content: Low Body Text Word Count (< 250 Words)",
                category="on_page",
                severity="medium",
                impact=0.6,
                confidence=0.75,
                estimated_effort=0.4,
                description="Pages contain fewer than 250 words of indexable body text.",
                why_it_matters="Search engines favor comprehensive, high-utility content that fully answers search intent. Thin pages often struggle to rank organically.",
                suggested_fix="Enrich the page with relevant explanations, FAQs, case studies, or user guides that satisfy visitor intent.",
                example_fix="Expand article or product description with helpful details, specifications, and FAQs.",
                priority_reason="Directly impacts search intent satisfaction and organic rankings.",
                evidences=evidences_thin_content,
            )
        )

    # 11. Missing Canonical Link Tag
    evidences_missing_canonical = []
    for p in crawled_pages:
        canonical = (p.get("canonical_url") or "").strip()
        if not canonical:
            evidences_missing_canonical.append(
                IssueFindingEvidence(
                    page_url=p["final_url"],
                    observed_value="No canonical link tag specified",
                    expected_value=f'<link rel="canonical" href="{p["final_url"]}">',
                    evidence_snippet='<link rel="canonical"> missing in <head>',
                    evidence_type="canonical",
                    explanation="The page lacks an explicit self-referential or authoritative canonical URL.",
                )
            )
    if evidences_missing_canonical:
        results.append(
            CheckResult(
                issue_code="WARN_CANONICAL_MISSING",
                title="Missing Canonical Link Element",
                category="on_page",
                severity="medium",
                impact=0.55,
                confidence=0.9,
                estimated_effort=0.1,
                description="The page HTML does not specify a canonical URL link tag.",
                why_it_matters="Canonical links prevent duplicate content penalties caused by tracking query parameters, URL casing, or trailing slash variations.",
                suggested_fix="Add a canonical tag pointing to the authoritative version of the page.",
                example_fix='<link rel="canonical" href="https://example.com/current-page">',
                priority_reason="Protects page authority against duplicate URL variations.",
                evidences=evidences_missing_canonical,
            )
        )

    # 12. Duplicate IDs on Page
    evidences_dup_ids = []
    for p in crawled_pages:
        dup_ids = p.get("duplicate_ids", [])
        if dup_ids:
            evidences_dup_ids.append(
                IssueFindingEvidence(
                    page_url=p["final_url"],
                    observed_value=f"Duplicate IDs: {', '.join(dup_ids[:5])}",
                    expected_value="HTML IDs must be unique per document",
                    evidence_snippet=f"Found duplicate ID attributes: {dup_ids[:3]}",
                    evidence_type="html_element",
                    explanation=f"Page has {len(dup_ids)} duplicate element IDs, violating W3C standards.",
                )
            )
    if evidences_dup_ids:
        results.append(
            CheckResult(
                issue_code="WARN_DUPLICATE_IDS",
                title="Duplicate HTML ID Attributes on Page",
                category="on_page",
                severity="low",
                impact=0.3,
                confidence=1.0,
                estimated_effort=0.15,
                description="Multiple elements share the same `id` attribute on the same page.",
                why_it_matters="Duplicate IDs break client-side JavaScript behaviors, CSS styling hooks, and screen reader element targeting.",
                suggested_fix="Ensure each ID attribute is globally unique on the page, or use CSS classes for non-unique styling targets.",
                example_fix="Use class='cta-button' instead of repeating id='cta-button' multiple times.",
                priority_reason="Ensures valid DOM structure and reliable frontend behavior.",
                evidences=evidences_dup_ids,
            )
        )

    return results
