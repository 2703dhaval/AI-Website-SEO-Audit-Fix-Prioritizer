import time
from urllib.parse import urljoin

import httpx

from app.core.config import settings
from app.core.ssrf import validate_url_ssrf


class FetchResult:
    def __init__(
        self,
        requested_url: str,
        final_url: str,
        status_code: int,
        headers: dict[str, str],
        text: str,
        response_time_ms: float,
        response_size_bytes: int,
        redirect_chain: list[str],
        content_type: str,
        is_html: bool,
        error: str | None = None,
    ):
        self.requested_url = requested_url
        self.final_url = final_url
        self.status_code = status_code
        self.headers = headers
        self.text = text
        self.response_time_ms = response_time_ms
        self.response_size_bytes = response_size_bytes
        self.redirect_chain = redirect_chain
        self.content_type = content_type
        self.is_html = is_html
        self.error = error


class SafeFetcher:
    def __init__(self, allow_test_mode: bool = False):
        self.allow_test_mode = allow_test_mode
        self.user_agent = settings.CRAWLER_USER_AGENT
        self.timeout = settings.REQUEST_TIMEOUT_SECONDS
        self.max_bytes = settings.MAX_RESPONSE_BYTES
        self.max_redirects = settings.MAX_REDIRECTS

    def fetch(self, url: str) -> FetchResult:
        current_url = url
        redirect_chain: list[str] = []
        start_time = time.time()

        for hop in range(self.max_redirects + 1):
            # 1. SSRF validation for current hop
            is_safe, resolved_ip, err = validate_url_ssrf(
                current_url, allow_test_mode=self.allow_test_mode
            )
            if not is_safe:
                elapsed_ms = (time.time() - start_time) * 1000
                return FetchResult(
                    requested_url=url,
                    final_url=current_url,
                    status_code=0,
                    headers={},
                    text="",
                    response_time_ms=elapsed_ms,
                    response_size_bytes=0,
                    redirect_chain=redirect_chain,
                    content_type="",
                    is_html=False,
                    error=f"SSRF Protection blocked destination {current_url}: {err}",
                )

            # 2. Execute single HTTP request without auto-following redirects
            try:
                with httpx.Client(
                    timeout=self.timeout,
                    headers={
                        "User-Agent": self.user_agent,
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.9",
                    },
                    follow_redirects=False,
                    verify=False if self.allow_test_mode else True,
                ) as client:
                    resp = client.get(current_url)
                    elapsed_ms = (time.time() - start_time) * 1000

                    status = resp.status_code
                    headers_dict = {k.lower(): v for k, v in resp.headers.items()}
                    content_type = headers_dict.get("content-type", "").lower()
                    is_html = (
                        "text/html" in content_type
                        or "application/xhtml+xml" in content_type
                    )

                    # Check for redirect status
                    if status in (301, 302, 303, 307, 308):
                        redirect_location = resp.headers.get("location")
                        if not redirect_location:
                            return FetchResult(
                                requested_url=url,
                                final_url=current_url,
                                status_code=status,
                                headers=headers_dict,
                                text="",
                                response_time_ms=elapsed_ms,
                                response_size_bytes=len(resp.content),
                                redirect_chain=redirect_chain,
                                content_type=content_type,
                                is_html=is_html,
                                error=f"Redirect {status} with missing Location header",
                            )

                        # Resolve relative redirect
                        next_url = urljoin(current_url, redirect_location)
                        redirect_chain.append(next_url)

                        # Check for redirect loop
                        if next_url in redirect_chain[:-1]:
                            return FetchResult(
                                requested_url=url,
                                final_url=next_url,
                                status_code=status,
                                headers=headers_dict,
                                text="",
                                response_time_ms=elapsed_ms,
                                response_size_bytes=len(resp.content),
                                redirect_chain=redirect_chain,
                                content_type=content_type,
                                is_html=is_html,
                                error=f"Redirect loop detected to {next_url}",
                            )

                        current_url = next_url
                        continue  # Follow next hop safely

                    # Non-redirect final response
                    # Enforce response body size limit
                    content_bytes = resp.content
                    if len(content_bytes) > self.max_bytes:
                        return FetchResult(
                            requested_url=url,
                            final_url=current_url,
                            status_code=status,
                            headers=headers_dict,
                            text="",
                            response_time_ms=elapsed_ms,
                            response_size_bytes=len(content_bytes),
                            redirect_chain=redirect_chain,
                            content_type=content_type,
                            is_html=is_html,
                            error=f"Response body exceeded {self.max_bytes} bytes limit",
                        )

                    text_content = resp.text if is_html or "xml" in content_type else ""

                    return FetchResult(
                        requested_url=url,
                        final_url=current_url,
                        status_code=status,
                        headers=headers_dict,
                        text=text_content,
                        response_time_ms=elapsed_ms,
                        response_size_bytes=len(content_bytes),
                        redirect_chain=redirect_chain,
                        content_type=content_type,
                        is_html=is_html,
                        error=None,
                    )

            except httpx.TimeoutException:
                elapsed_ms = (time.time() - start_time) * 1000
                return FetchResult(
                    requested_url=url,
                    final_url=current_url,
                    status_code=0,
                    headers={},
                    text="",
                    response_time_ms=elapsed_ms,
                    response_size_bytes=0,
                    redirect_chain=redirect_chain,
                    content_type="",
                    is_html=False,
                    error=f"Request timed out after {self.timeout} seconds",
                )
            except httpx.RequestError as exc:
                elapsed_ms = (time.time() - start_time) * 1000
                return FetchResult(
                    requested_url=url,
                    final_url=current_url,
                    status_code=0,
                    headers={},
                    text="",
                    response_time_ms=elapsed_ms,
                    response_size_bytes=0,
                    redirect_chain=redirect_chain,
                    content_type="",
                    is_html=False,
                    error=f"Network error: {exc!s}",
                )

        # Exceeded max redirects
        elapsed_ms = (time.time() - start_time) * 1000
        return FetchResult(
            requested_url=url,
            final_url=current_url,
            status_code=310,
            headers={},
            text="",
            response_time_ms=elapsed_ms,
            response_size_bytes=0,
            redirect_chain=redirect_chain,
            content_type="",
            is_html=False,
            error=f"Exceeded maximum redirect limit of {self.max_redirects} hops",
        )
