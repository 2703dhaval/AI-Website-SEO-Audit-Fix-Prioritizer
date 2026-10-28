import pytest
from app.crawler.parser import normalize_url, is_same_origin, parse_html_page


class TestCrawlerParser:
    def test_normalize_url(self):
        base = "https://example.com/blog/article-1"
        assert normalize_url("/contact", base) == "https://example.com/contact"
        assert normalize_url("../about", base) == "https://example.com/about"
        assert normalize_url("page#section-2", base) == "https://example.com/blog/page"
        assert normalize_url("https://example.com/services?ref=nav", base) == "https://example.com/services?ref=nav"
        assert normalize_url("javascript:void(0)", base) is None
        assert normalize_url("mailto:test@example.com", base) is None
        assert normalize_url("tel:+123456789", base) is None
        assert normalize_url("#top", base) is None

    def test_is_same_origin(self):
        root = "scalezix.com"
        assert is_same_origin("https://scalezix.com/about", root) is True
        assert is_same_origin("https://www.scalezix.com/services", root) is True
        assert is_same_origin("https://otherdomain.com/page", root) is False
        assert is_same_origin("https://subdomain.scalezix.com", root) is False

    def test_parse_html_page_metadata(self):
        html = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Custom Software Engineering | Scalezix</title>
            <meta name="description" content="Scalezix provides enterprise AI and scalable backend software engineering.">
            <meta name="robots" content="index, follow">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="canonical" href="https://scalezix.com/">
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "Scalezix"
            }
            </script>
        </head>
        <body>
            <div id="wrapper">
                <h1 id="main-heading">Empowering Innovation</h1>
                <p>Scalezix builds fast, resilient cloud applications for forward-thinking clients.</p>
                <img src="/logo.png" alt="Scalezix Logo" width="200" height="50">
                <img src="/unlabeled.jpg">
                <a href="/services">Our Services</a>
                <a href="https://external.com/partner">Partner</a>
            </div>
            <div id="wrapper">Duplicate ID here</div>
        </body>
        </html>"""

        data = parse_html_page(html, "https://scalezix.com/", "scalezix.com")
        assert data.language == "en"
        assert data.title == "Custom Software Engineering | Scalezix"
        assert "enterprise AI" in data.meta_description
        assert data.canonical_url == "https://scalezix.com/"
        assert data.robots_meta == "index, follow"
        assert data.viewport == "width=device-width, initial-scale=1.0"
        assert data.h1_list == ["Empowering Innovation"]
        assert len(data.images) == 2
        assert data.images[0]["has_alt"] is True
        assert data.images[1]["has_alt"] is False
        assert "wrapper" in data.duplicate_ids
        assert len(data.json_ld_scripts) == 1
        assert data.json_ld_scripts[0]["parsed"]["name"] == "Scalezix"
        assert data.word_count > 10
        assert len(data.internal_links) == 1
        assert data.internal_links[0]["href"] == "https://scalezix.com/services"
        assert len(data.external_links) == 1
        assert data.external_links[0]["href"] == "https://external.com/partner"

    def test_parse_html_malformed_json_ld(self):
        html = """<html><head>
        <script type="application/ld+json">
        { "name": "Broken JSON", trailing_comma: true, }
        </script>
        </head></html>"""
        data = parse_html_page(html, "https://example.com/", "example.com")
        assert len(data.json_ld_scripts) == 1
        assert data.json_ld_scripts[0]["error"] is not None
