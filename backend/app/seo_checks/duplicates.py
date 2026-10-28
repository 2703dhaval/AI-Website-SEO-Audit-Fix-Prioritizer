import re
from collections import defaultdict
from typing import Any

from app.seo_checks.base import CheckResult, IssueFindingEvidence


def get_token_shingles(text: str, n: int = 3) -> set[str]:
    """Generates word n-grams (shingles) for text similarity calculation."""
    tokens = [w.lower() for w in re.findall(r"\b\w{3,}\b", text)]
    if len(tokens) < n:
        return set(tokens)
    return set(" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1))


def jaccard_similarity(set_a: set[str], set_b: set[str]) -> float:
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union if union > 0 else 0.0


def check_duplicates(crawled_pages: list[dict[str, Any]]) -> list[CheckResult]:
    results = []

    # 1. Duplicate Page Titles
    titles_map = defaultdict(list)
    for p in crawled_pages:
        title = (p.get("title") or "").strip()
        if title:
            titles_map[title.lower()].append(p["final_url"])

    dup_title_evidences = []
    for title_lower, urls in titles_map.items():
        if len(urls) > 1:
            for url in urls:
                other_urls = [u for u in urls if u != url]
                dup_title_evidences.append(
                    IssueFindingEvidence(
                        page_url=url,
                        observed_value=f"Shared title across {len(urls)} pages: '{title_lower}'",
                        expected_value="Every page should possess a unique, distinct title tag",
                        evidence_snippet=f"Duplicate title also on: {', '.join(other_urls[:2])}",
                        evidence_type="title_tag",
                        explanation=f"Identical title tag found on {len(urls)} separate pages.",
                    )
                )

    if dup_title_evidences:
        results.append(
            CheckResult(
                issue_code="ERR_DUPLICATE_TITLE",
                title="Duplicate Page Title Tags Across Multiple Pages",
                category="duplicates",
                severity="high",
                impact=0.75,
                confidence=1.0,
                estimated_effort=0.2,
                description="Multiple pages on the website share the exact same title tag.",
                why_it_matters="Duplicate titles cause search engine keyword cannibalization where your own pages compete against one another in search rankings.",
                suggested_fix="Create distinct, topic-specific title tags for every page.",
                example_fix="Include product name, category name, or location modifier in each page title.",
                priority_reason="Resolves keyword cannibalization across the domain.",
                evidences=dup_title_evidences,
            )
        )

    # 2. Duplicate Meta Descriptions
    desc_map = defaultdict(list)
    for p in crawled_pages:
        desc = (p.get("meta_description") or "").strip()
        if desc:
            desc_map[desc.lower()].append(p["final_url"])

    dup_desc_evidences = []
    for desc_lower, urls in desc_map.items():
        if len(urls) > 1:
            for url in urls:
                other_urls = [u for u in urls if u != url]
                dup_desc_evidences.append(
                    IssueFindingEvidence(
                        page_url=url,
                        observed_value=f"Shared meta description across {len(urls)} pages",
                        expected_value="Unique meta description per indexable page",
                        evidence_snippet=f"Matches: {', '.join(other_urls[:2])}",
                        evidence_type="meta_description",
                        explanation=f"Identical meta description used on {len(urls)} pages.",
                    )
                )

    if dup_desc_evidences:
        results.append(
            CheckResult(
                issue_code="WARN_DUPLICATE_META_DESC",
                title="Duplicate Meta Descriptions Across Multiple Pages",
                category="duplicates",
                severity="medium",
                impact=0.5,
                confidence=1.0,
                estimated_effort=0.2,
                description="Multiple pages share the exact same meta description tag.",
                why_it_matters="Fails to highlight unique page benefits in search snippets, reducing CTR.",
                suggested_fix="Customize meta descriptions to highlight the specific content of each page.",
                example_fix="Craft tailored description highlighting unique page offerings.",
                priority_reason="Improves SERP relevance across site pages.",
                evidences=dup_desc_evidences,
            )
        )

    # 3. Duplicate Content Candidates (Shingle Jaccard Similarity > 0.85)
    # Check text shingles for pages with word count > 50
    eligible_pages = [
        p for p in crawled_pages if p.get("word_count", 0) >= 50 and p.get("clean_text")
    ]
    dup_content_evidences = []
    seen_pairs = set()

    # Precompute shingles
    page_shingles = {
        p["final_url"]: get_token_shingles(p.get("clean_text", ""))
        for p in eligible_pages
    }

    for i in range(len(eligible_pages)):
        url_a = eligible_pages[i]["final_url"]
        shingles_a = page_shingles[url_a]
        if not shingles_a:
            continue

        for j in range(i + 1, len(eligible_pages)):
            url_b = eligible_pages[j]["final_url"]
            shingles_b = page_shingles[url_b]
            if not shingles_b:
                continue

            pair_key = tuple(sorted([url_a, url_b]))
            if pair_key in seen_pairs:
                continue

            similarity = jaccard_similarity(shingles_a, shingles_b)
            if similarity >= 0.85:
                seen_pairs.add(pair_key)
                dup_content_evidences.append(
                    IssueFindingEvidence(
                        page_url=url_a,
                        observed_value=f"{int(similarity * 100)}% content similarity with {url_b}",
                        expected_value="Distinct, differentiated page content",
                        evidence_snippet=f"Jaccard shingle similarity index: {similarity:.2f}",
                        evidence_type="text_content",
                        explanation=f"Body text is near-duplicate ({int(similarity * 100)}% match) of {url_b}.",
                    )
                )
                dup_content_evidences.append(
                    IssueFindingEvidence(
                        page_url=url_b,
                        observed_value=f"{int(similarity * 100)}% content similarity with {url_a}",
                        expected_value="Distinct, differentiated page content",
                        evidence_snippet=f"Jaccard shingle similarity index: {similarity:.2f}",
                        evidence_type="text_content",
                        explanation=f"Body text is near-duplicate ({int(similarity * 100)}% match) of {url_a}.",
                    )
                )

    if dup_content_evidences:
        results.append(
            CheckResult(
                issue_code="WARN_DUPLICATE_CONTENT",
                title="Near-Duplicate Content Detected Between Pages (> 85% Similarity)",
                category="duplicates",
                severity="high",
                impact=0.75,
                confidence=0.85,
                estimated_effort=0.45,
                description="Multiple pages share substantially identical body text content.",
                why_it_matters="Search engines filter out near-duplicate pages from indexing or consolidate ranking signals unpredictably.",
                suggested_fix="Consolidate duplicate pages using 301 redirects or canonical tags, or significantly differentiate their content.",
                example_fix='Add <link rel="canonical" href="https://example.com/master-page"> or merge content.',
                priority_reason="Prevents indexing dilution and search engine filtering.",
                evidences=dup_content_evidences,
            )
        )

    return results
