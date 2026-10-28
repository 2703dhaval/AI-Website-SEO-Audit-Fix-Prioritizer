import pytest
from app.crawler.crawler import WebCrawler
from app.seo_checks.runner import run_all_seo_checks


class TestCrawlPipelineLive:
    def test_live_crawl_against_local_test_site(self, local_test_site):
        # local_test_site is "http://127.0.0.1:8765"
        crawler = WebCrawler(
            start_url=local_test_site,
            max_pages=20,
            max_depth=3,
            crawl_delay=0.0,
            allow_test_mode=True
        )
        result = crawler.crawl()
        assert result["status"] == "completed"
        assert result["total_crawled"] >= 5

        crawled_pages = result["crawled_pages"]
        robots_summary = result["robots_summary"]

        # Run all SEO detection checks on the crawled pages
        findings = run_all_seo_checks(crawled_pages, robots_summary)
        issue_codes = {f.issue_code for f in findings}

        # Verify key intentional issues were detected from the test site
        assert "ERR_TITLE_MISSING" in issue_codes, "Should detect page missing title"
        assert "ERR_META_DESC_MISSING" in issue_codes, "Should detect page missing meta description"
        assert "ERR_H1_MISSING" in issue_codes, "Should detect page missing H1"
        assert "ERR_IMG_ALT_MISSING" in issue_codes, "Should detect image missing alt"
        assert "ERR_HTTP_4XX" in issue_codes, "Should detect 404 broken link page"
        assert "ERR_DUPLICATE_TITLE" in issue_codes, "Should detect duplicate titles on pages 1 & 2"
        assert "INFO_PAGE_NOINDEX" in issue_codes, "Should detect noindex directive on test page"
