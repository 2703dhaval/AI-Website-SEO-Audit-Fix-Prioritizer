import urllib.robotparser
from urllib.parse import urljoin, urlparse

import httpx

from app.core.config import settings
from app.core.ssrf import validate_url_ssrf


class RobotsTxtPolicy:
    def __init__(self, target_url: str, allow_test_mode: bool = False):
        self.target_url = target_url
        self.allow_test_mode = allow_test_mode
        self.parsed_url = urlparse(target_url)
        self.origin = f"{self.parsed_url.scheme}://{self.parsed_url.netloc}"
        self.robots_url = urljoin(self.origin, "/robots.txt")
        self.parser = urllib.robotparser.RobotFileParser()
        self.parser.set_url(self.robots_url)
        self.status_code: int | None = None
        self.fetched_successfully: bool = False
        self.sitemaps: list[str] = []
        self.crawl_delay: float | None = None
        self.raw_content: str = ""

    def fetch_and_parse(self) -> tuple[bool, str]:
        """
        Retrieves robots.txt securely with SSRF checks.
        Returns (success, summary_message).
        """
        is_safe, _, err = validate_url_ssrf(
            self.robots_url, allow_test_mode=self.allow_test_mode
        )
        if not is_safe:
            return False, f"Robots.txt SSRF check failed: {err}"

        try:
            with httpx.Client(
                timeout=settings.REQUEST_TIMEOUT_SECONDS,
                headers={"User-Agent": settings.CRAWLER_USER_AGENT},
                follow_redirects=True,
                verify=False if self.allow_test_mode else True,
            ) as client:
                resp = client.get(self.robots_url)
                self.status_code = resp.status_code

                if resp.status_code == 200:
                    self.raw_content = resp.text
                    lines = resp.text.splitlines()
                    self.parser.parse(lines)
                    self.fetched_successfully = True

                    # Extract sitemaps and crawl delay
                    for line in lines:
                        clean_line = line.strip()
                        if clean_line.lower().startswith("sitemap:"):
                            sitemap_url = clean_line.split(":", 1)[1].strip()
                            self.sitemaps.append(sitemap_url)
                        elif clean_line.lower().startswith("crawl-delay:"):
                            try:
                                self.crawl_delay = float(
                                    clean_line.split(":", 1)[1].strip()
                                )
                            except ValueError:
                                pass

                    return (
                        True,
                        f"robots.txt successfully retrieved (Status 200). Found {len(self.sitemaps)} sitemaps.",
                    )
                elif resp.status_code == 404:
                    return (
                        True,
                        "No robots.txt found (Status 404). Site allows general crawling.",
                    )
                elif resp.status_code in (401, 403):
                    return (
                        False,
                        f"robots.txt returned status {resp.status_code}. Site restricts automated access.",
                    )
                else:
                    return (
                        False,
                        f"robots.txt returned unexpected HTTP status {resp.status_code}.",
                    )
        except Exception as e:
            # Under network errors or connection failure, handle conservatively
            return False, f"Failed to retrieve robots.txt: {e!s}"

    def can_fetch(self, url: str) -> bool:
        """Checks if the declared user-agent is permitted to crawl the URL."""
        if not self.fetched_successfully:
            # If robots.txt returned 404, standard policy is permitted.
            if self.status_code == 404:
                return True
            # For network error or 403, proceed conservatively or permit root
            return True
        return self.parser.can_fetch(settings.CRAWLER_USER_AGENT, url)
