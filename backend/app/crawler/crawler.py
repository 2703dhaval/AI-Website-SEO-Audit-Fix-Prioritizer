import time
from collections import deque
from collections.abc import Callable
from typing import Any
from urllib.parse import urlparse

from app.core.config import settings
from app.crawler.fetcher import FetchResult, SafeFetcher
from app.crawler.parser import parse_html_page
from app.crawler.robots import RobotsTxtPolicy


class WebCrawler:
    def __init__(
        self,
        start_url: str,
        max_pages: int = 25,
        max_depth: int = 3,
        crawl_delay: float = 0.5,
        exclude_patterns: list[str] | None = None,
        allow_test_mode: bool = False,
        on_progress: Callable[[dict[str, Any]], None] | None = None,
        is_cancelled: Callable[[], bool] | None = None,
    ):
        self.start_url = start_url
        self.max_pages = min(max_pages, settings.MAX_CRAWL_PAGES)
        self.max_depth = min(max_depth, settings.MAX_CRAWL_DEPTH)
        self.crawl_delay = crawl_delay
        self.exclude_patterns = exclude_patterns or []
        self.allow_test_mode = allow_test_mode
        self.on_progress = on_progress
        self.is_cancelled = is_cancelled

        parsed = urlparse(start_url)
        self.root_hostname = parsed.hostname or ""
        self.fetcher = SafeFetcher(allow_test_mode=self.allow_test_mode)
        self.robots_policy = RobotsTxtPolicy(
            start_url, allow_test_mode=self.allow_test_mode
        )

    def is_excluded(self, url: str) -> bool:
        for pat in self.exclude_patterns:
            if pat and pat in url:
                return True
        return False

    def crawl(self) -> dict[str, Any]:
        """
        Executes safe, BFS-oriented website crawl with SSRF protections,
        robots.txt compliance, and rate limiting.
        """
        # Step 1: Robots.txt inspection
        robots_ok, robots_msg = self.robots_policy.fetch_and_parse()
        robots_summary = {
            "robots_url": self.robots_policy.robots_url,
            "fetched_successfully": self.robots_policy.fetched_successfully,
            "status_code": self.robots_policy.status_code,
            "summary": robots_msg,
            "sitemaps": self.robots_policy.sitemaps,
            "crawl_delay": self.robots_policy.crawl_delay,
        }

        # Apply crawl delay if specified in robots.txt and slower than default
        if (
            self.robots_policy.crawl_delay
            and self.robots_policy.crawl_delay > self.crawl_delay
        ):
            self.crawl_delay = min(self.robots_policy.crawl_delay, 3.0)

        # Step 2: Initialize queue: (url, depth)
        queue = deque([(self.start_url, 0)])
        discovered_urls: set[str] = {self.start_url}
        visited_urls: set[str] = set()

        crawled_pages_data: list[dict[str, Any]] = []
        events_log: list[dict[str, Any]] = []

        def log_event(event_type: str, message: str, url: str | None = None):
            events_log.append(
                {
                    "event_type": event_type,
                    "message": message,
                    "url": url,
                    "timestamp": time.time(),
                }
            )

        log_event(
            "info",
            f"Started crawl for {self.start_url}. Crawl limit: {self.max_pages} pages, Depth: {self.max_depth}",
        )
        log_event("robots", robots_msg, self.robots_policy.robots_url)

        # Check start URL robots permission
        if not self.robots_policy.can_fetch(self.start_url):
            log_event(
                "error",
                f"Seed URL {self.start_url} is disallowed by robots.txt",
                self.start_url,
            )
            return {
                "crawled_pages": [],
                "robots_summary": robots_summary,
                "events": events_log,
                "total_discovered": 1,
                "total_crawled": 0,
                "status": "completed",
                "error": "Seed URL disallowed by robots.txt",
            }

        while queue and len(crawled_pages_data) < self.max_pages:
            # Check cooperative cancellation
            if self.is_cancelled and self.is_cancelled():
                log_event("cancel", "Audit crawl cancelled by user request.")
                return {
                    "crawled_pages": crawled_pages_data,
                    "robots_summary": robots_summary,
                    "events": events_log,
                    "total_discovered": len(discovered_urls),
                    "total_crawled": len(crawled_pages_data),
                    "status": "cancelled",
                    "error": "Crawl cancelled by user",
                }

            current_url, depth = queue.popleft()
            if current_url in visited_urls:
                continue

            visited_urls.add(current_url)

            # Check robots.txt
            if not self.robots_policy.can_fetch(current_url):
                log_event(
                    "blocked_by_robots",
                    f"Skipping {current_url} per robots.txt directive",
                    current_url,
                )
                crawled_pages_data.append(
                    {
                        "requested_url": current_url,
                        "final_url": current_url,
                        "canonical_url": None,
                        "http_status": 403,
                        "title": None,
                        "meta_description": None,
                        "h1_list": [],
                        "language": None,
                        "robots_directives": "blocked_by_robots",
                        "word_count": 0,
                        "internal_links": [],
                        "external_links": [],
                        "images": [],
                        "headings": [],
                        "duplicate_ids": [],
                        "json_ld_scripts": [],
                        "response_time_ms": 0.0,
                        "response_size_bytes": 0,
                        "crawl_depth": depth,
                        "indexability_status": "blocked_by_robots",
                        "redirect_chain": [],
                        "clean_text": "",
                    }
                )
                continue

            # Fetch page safely
            fetch_res: FetchResult = self.fetcher.fetch(current_url)

            if fetch_res.error:
                log_event(
                    "error",
                    f"Fetch failed for {current_url}: {fetch_res.error}",
                    current_url,
                )
                crawled_pages_data.append(
                    {
                        "requested_url": current_url,
                        "final_url": fetch_res.final_url or current_url,
                        "canonical_url": None,
                        "http_status": fetch_res.status_code or 0,
                        "title": None,
                        "meta_description": None,
                        "h1_list": [],
                        "language": None,
                        "robots_directives": None,
                        "word_count": 0,
                        "internal_links": [],
                        "external_links": [],
                        "images": [],
                        "headings": [],
                        "duplicate_ids": [],
                        "json_ld_scripts": [],
                        "response_time_ms": fetch_res.response_time_ms,
                        "response_size_bytes": fetch_res.response_size_bytes,
                        "crawl_depth": depth,
                        "indexability_status": "error",
                        "redirect_chain": fetch_res.redirect_chain,
                        "clean_text": "",
                    }
                )
                continue

            # If page is HTML, parse structure and discover links
            parsed_data = None
            if fetch_res.is_html and fetch_res.text:
                parsed_data = parse_html_page(
                    fetch_res.text, fetch_res.final_url, self.root_hostname
                )

                # Determine indexability
                directives = (
                    parsed_data.robots_meta
                    or fetch_res.headers.get("x-robots-tag")
                    or ""
                ).lower()
                if "noindex" in directives:
                    index_status = "noindex"
                elif fetch_res.status_code != 200:
                    index_status = "error"
                elif (
                    parsed_data.canonical_url
                    and parsed_data.canonical_url != fetch_res.final_url
                ):
                    index_status = "canonicalized"
                else:
                    index_status = "indexable"

                page_record = {
                    "requested_url": current_url,
                    "final_url": fetch_res.final_url,
                    "canonical_url": parsed_data.canonical_url,
                    "http_status": fetch_res.status_code,
                    "title": parsed_data.title,
                    "meta_description": parsed_data.meta_description,
                    "h1_list": parsed_data.h1_list,
                    "headings": parsed_data.headings,
                    "language": parsed_data.language,
                    "robots_directives": directives if directives else None,
                    "viewport": parsed_data.viewport,
                    "word_count": parsed_data.word_count,
                    "internal_links": parsed_data.internal_links,
                    "external_links": parsed_data.external_links,
                    "images": parsed_data.images,
                    "duplicate_ids": parsed_data.duplicate_ids,
                    "json_ld_scripts": parsed_data.json_ld_scripts,
                    "response_time_ms": fetch_res.response_time_ms,
                    "response_size_bytes": fetch_res.response_size_bytes,
                    "crawl_depth": depth,
                    "indexability_status": index_status,
                    "redirect_chain": fetch_res.redirect_chain,
                    "clean_text": parsed_data.clean_text,
                }
                crawled_pages_data.append(page_record)
                log_event(
                    "crawl_page",
                    f"Crawled ({fetch_res.status_code}) {fetch_res.final_url} (depth {depth})",
                    fetch_res.final_url,
                )

                # Enqueue newly discovered internal links if within max depth
                if depth < self.max_depth:
                    for disc_url in parsed_data.discovered_internal_urls:
                        if disc_url not in discovered_urls and not self.is_excluded(
                            disc_url
                        ):
                            discovered_urls.add(disc_url)
                            queue.append((disc_url, depth + 1))
            else:
                # Non-HTML or empty response
                page_record = {
                    "requested_url": current_url,
                    "final_url": fetch_res.final_url,
                    "canonical_url": None,
                    "http_status": fetch_res.status_code,
                    "title": None,
                    "meta_description": None,
                    "h1_list": [],
                    "headings": [],
                    "language": None,
                    "robots_directives": None,
                    "viewport": None,
                    "word_count": 0,
                    "internal_links": [],
                    "external_links": [],
                    "images": [],
                    "duplicate_ids": [],
                    "json_ld_scripts": [],
                    "response_time_ms": fetch_res.response_time_ms,
                    "response_size_bytes": fetch_res.response_size_bytes,
                    "crawl_depth": depth,
                    "indexability_status": "error"
                    if fetch_res.status_code >= 400
                    else "non_html",
                    "redirect_chain": fetch_res.redirect_chain,
                    "clean_text": "",
                }
                crawled_pages_data.append(page_record)
                log_event(
                    "crawl_page",
                    f"Fetched non-HTML/response ({fetch_res.status_code}) {current_url}",
                    current_url,
                )

            # Emit progress update callback
            if self.on_progress:
                self.on_progress(
                    {
                        "pages_crawled": len(crawled_pages_data),
                        "pages_discovered": len(discovered_urls),
                        "current_url": current_url,
                        "queue_length": len(queue),
                        "status": "running",
                    }
                )

            # Respect configurable rate-limiting crawl delay
            if self.crawl_delay > 0:
                time.sleep(self.crawl_delay)

        log_event("complete", f"Finished crawling {len(crawled_pages_data)} pages.")
        return {
            "crawled_pages": crawled_pages_data,
            "robots_summary": robots_summary,
            "events": events_log,
            "total_discovered": len(discovered_urls),
            "total_crawled": len(crawled_pages_data),
            "status": "completed",
            "error": None,
        }
