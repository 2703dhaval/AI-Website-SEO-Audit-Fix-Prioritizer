import pytest
from app.seo_checks.crawlability import check_crawlability
from app.seo_checks.on_page import check_on_page
from app.seo_checks.internal_links import check_internal_links
from app.seo_checks.structured_data import check_structured_data
from app.seo_checks.performance import check_performance
from app.seo_checks.duplicates import check_duplicates


class TestSEOChecks:
    def test_on_page_missing_title_and_meta(self):
        pages = [{
            "final_url": "https://example.com/no-meta",
            "title": "",
            "meta_description": "",
            "h1_list": [],
            "headings": [],
            "images": [],
            "viewport": "",
            "language": "",
            "word_count": 50,
            "canonical_url": "",
            "duplicate_ids": [],
            "http_status": 200
        }]
        findings = check_on_page(pages)
        codes = [f.issue_code for f in findings]
        assert "ERR_TITLE_MISSING" in codes
        assert "ERR_META_DESC_MISSING" in codes
        assert "ERR_H1_MISSING" in codes
        assert "ERR_VIEWPORT_MISSING" in codes
        assert "WARN_LANG_MISSING" in codes
        assert "WARN_CANONICAL_MISSING" in codes
        assert "WARN_THIN_CONTENT" in codes

    def test_on_page_missing_alt_and_heading_hierarchy(self):
        pages = [{
            "final_url": "https://example.com/headings-and-images",
            "title": "Optimized Page Title With Sufficient Length Here",
            "meta_description": "A well-written descriptive meta summary providing plenty of context for search bot crawlers.",
            "h1_list": ["Primary H1"],
            "headings": [
                {"tag": "h1", "text": "Primary H1"},
                {"tag": "h4", "text": "Skipped to H4"}  # Heading skip!
            ],
            "images": [
                {"src": "/pic1.jpg", "has_alt": False, "alt": ""},
                {"src": "/pic2.jpg", "has_alt": True, "alt": "Valid alt"}
            ],
            "viewport": "width=device-width, initial-scale=1.0",
            "language": "en",
            "word_count": 450,
            "canonical_url": "https://example.com/headings-and-images",
            "duplicate_ids": [],
            "http_status": 200
        }]
        findings = check_on_page(pages)
        codes = [f.issue_code for f in findings]
        assert "ERR_IMG_ALT_MISSING" in codes
        assert "WARN_HEADING_HIERARCHY" in codes

    def test_crawlability_4xx_and_redirect_chains(self):
        pages = [
            {
                "final_url": "https://example.com/broken",
                "requested_url": "https://example.com/broken",
                "http_status": 404,
                "redirect_chain": []
            },
            {
                "final_url": "https://example.com/final-dest",
                "requested_url": "https://example.com/initial",
                "http_status": 200,
                "redirect_chain": ["https://example.com/hop1", "https://example.com/final-dest"]
            }
        ]
        findings = check_crawlability(pages, {"fetched_successfully": True, "status_code": 200})
        codes = [f.issue_code for f in findings]
        assert "ERR_HTTP_4XX" in codes
        assert "WARN_REDIRECT_CHAIN" in codes

    def test_internal_links_broken_link_and_redirects(self):
        pages = [
            {
                "final_url": "https://example.com/",
                "internal_links": [
                    {"href": "https://example.com/404-page", "text": "Broken Link"},
                    {"href": "https://example.com/redirect-target", "text": "Redirect Link"},
                    {"href": "https://example.com/normal", "text": ""}  # Empty anchor text!
                ],
                "crawl_depth": 0
            },
            {
                "final_url": "https://example.com/404-page",
                "http_status": 404,
                "internal_links": [],
                "crawl_depth": 1,
                "redirect_chain": []
            },
            {
                "final_url": "https://example.com/redirect-target",
                "http_status": 200,
                "internal_links": [],
                "crawl_depth": 1,
                "redirect_chain": ["https://example.com/redirect-target"]
            },
            {
                "final_url": "https://example.com/normal",
                "http_status": 200,
                "internal_links": [],
                "crawl_depth": 1,
                "redirect_chain": []
            }
        ]
        findings = check_internal_links(pages)
        codes = [f.issue_code for f in findings]
        assert "ERR_BROKEN_INTERNAL_LINK" in codes
        assert "WARN_INTERNAL_LINK_TO_REDIRECT" in codes
        assert "WARN_EMPTY_ANCHOR_TEXT" in codes

    def test_structured_data_syntax_errors(self):
        pages = [{
            "final_url": "https://example.com/schema-test",
            "http_status": 200,
            "json_ld_scripts": [
                {"raw": "{broken_json}", "parsed": None, "error": "Expecting property name enclosed in double quotes"}
            ]
        }]
        findings = check_structured_data(pages)
        codes = [f.issue_code for f in findings]
        assert "ERR_JSONLD_SYNTAX" in codes

    def test_duplicates_titles_and_content(self):
        pages = [
            {
                "final_url": "https://example.com/page-1",
                "title": "Exact Duplicate Title Across Both Pages",
                "meta_description": "Shared meta description",
                "word_count": 80,
                "clean_text": "Scalezix builds artificial intelligence and high scalability systems for cloud enterprise clients with modern technology."
            },
            {
                "final_url": "https://example.com/page-2",
                "title": "Exact Duplicate Title Across Both Pages",
                "meta_description": "Shared meta description",
                "word_count": 80,
                "clean_text": "Scalezix builds artificial intelligence and high scalability systems for cloud enterprise clients with modern technology."
            }
        ]
        findings = check_duplicates(pages)
        codes = [f.issue_code for f in findings]
        assert "ERR_DUPLICATE_TITLE" in codes
        assert "WARN_DUPLICATE_META_DESC" in codes
        assert "WARN_DUPLICATE_CONTENT" in codes
