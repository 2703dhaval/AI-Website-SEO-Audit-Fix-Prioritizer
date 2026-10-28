import json
import re
from typing import Any
from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup


def normalize_url(url: str, base_url: str) -> str | None:
    """
    Normalizes a discovered link:
    - Joins with base_url
    - Strips fragment (#...)
    - Converts scheme and hostname to lowercase
    - Rejects javascript:, mailto:, tel:, data: schemes
    """
    if not url or not isinstance(url, str):
        return None
    url = url.strip()
    if url.startswith(("javascript:", "mailto:", "tel:", "data:", "#")):
        return None

    try:
        joined = urljoin(base_url, url)
        defragged, _ = urldefrag(joined)
        parsed = urlparse(defragged)
        if parsed.scheme.lower() not in ("http", "https"):
            return None
        if not parsed.hostname:
            return None

        # Rebuild clean URL
        hostname = parsed.hostname.lower()
        port_part = (
            f":{parsed.port}" if parsed.port and parsed.port not in (80, 443) else ""
        )
        path = parsed.path or "/"
        query_part = f"?{parsed.query}" if parsed.query else ""
        return f"{parsed.scheme.lower()}://{hostname}{port_part}{path}{query_part}"
    except Exception:
        return None


def is_same_origin(url: str, root_hostname: str) -> bool:
    """Verifies whether the link belongs to the target domain."""
    try:
        parsed = urlparse(url)
        if not parsed.hostname:
            return False
        host = parsed.hostname.lower()
        root = root_hostname.lower()
        return host == root or host == f"www.{root}" or f"www.{host}" == root
    except Exception:
        return False


class ParsedPageData:
    def __init__(self):
        self.title: str | None = None
        self.meta_description: str | None = None
        self.canonical_url: str | None = None
        self.robots_meta: str | None = None
        self.language: str | None = None
        self.viewport: str | None = None

        self.h1_list: list[str] = []
        self.headings: list[dict[str, Any]] = []  # tag: h1-h6, text
        self.images: list[dict[str, Any]] = []  # src, alt, has_alt, width, height
        self.duplicate_ids: list[str] = []
        self.json_ld_scripts: list[dict[str, Any]] = []  # raw_text, parsed_json, error

        self.word_count: int = 0
        self.clean_text: str = ""
        self.internal_links: list[dict[str, str]] = []  # href, text, is_relative
        self.external_links: list[dict[str, str]] = []  # href, text
        self.discovered_internal_urls: set[str] = set()


def parse_html_page(
    html_text: str, current_url: str, root_hostname: str
) -> ParsedPageData:
    data = ParsedPageData()
    if not html_text:
        return data

    try:
        soup = BeautifulSoup(html_text, "html.parser")
    except Exception:
        return data

    # 1. <html> lang attribute
    html_tag = soup.find("html")
    if html_tag and html_tag.get("lang"):
        data.language = str(html_tag["lang"]).strip()

    # 2. <title>
    title_tag = soup.find("title")
    if title_tag:
        data.title = title_tag.get_text(strip=True)

    # 3. Meta tags
    for meta in soup.find_all("meta"):
        name = meta.get("name", "").lower()
        prop = meta.get("property", "").lower()
        content = meta.get("content", "").strip()

        if name == "description" or prop == "og:description":
            if not data.meta_description and content:
                data.meta_description = content
        elif name == "robots":
            data.robots_meta = content.lower()
        elif name == "viewport":
            data.viewport = content

    # 4. Canonical link
    canonical_link = soup.find("link", rel=lambda r: r and "canonical" in r)
    if canonical_link and canonical_link.get("href"):
        data.canonical_url = canonical_link["href"].strip()

    # 5. Headings
    for h in soup.find_all(re.compile(r"^h[1-6]$", re.IGNORECASE)):
        tag_name = h.name.lower()
        h_text = h.get_text(strip=True)
        data.headings.append({"tag": tag_name, "text": h_text})
        if tag_name == "h1":
            data.h1_list.append(h_text)

    # 6. Images
    for img in soup.find_all("img"):
        src = img.get("src", "").strip()
        alt = img.get("alt")
        has_alt = alt is not None
        alt_text = alt.strip() if has_alt else ""
        width = img.get("width")
        height = img.get("height")
        data.images.append(
            {
                "src": src,
                "alt": alt_text,
                "has_alt": has_alt,
                "is_decorative": has_alt
                and alt_text == ""
                and img.get("role") == "presentation",
                "has_dimensions": bool(width and height),
            }
        )

    # 7. Duplicate IDs
    seen_ids = set()
    dup_ids = set()
    for tag in soup.find_all(id=True):
        tag_id = tag["id"].strip()
        if tag_id:
            if tag_id in seen_ids:
                dup_ids.add(tag_id)
            seen_ids.add(tag_id)
    data.duplicate_ids = list(dup_ids)

    # 8. Structured data: JSON-LD
    for script in soup.find_all(
        "script", type=lambda t: t and "application/ld+json" in t.lower()
    ):
        raw = script.get_text(strip=True)
        try:
            parsed_json = json.loads(raw)
            data.json_ld_scripts.append(
                {"raw": raw, "parsed": parsed_json, "error": None}
            )
        except Exception as e:
            data.json_ld_scripts.append({"raw": raw, "parsed": None, "error": str(e)})

    # 9. Clean text & Word count
    # Remove script, style, noscript, svg
    for el in soup(["script", "style", "noscript", "svg"]):
        el.extract()
    body = soup.find("body")
    if body:
        text = body.get_text(separator=" ", strip=True)
    else:
        text = soup.get_text(separator=" ", strip=True)
    data.clean_text = text
    words = re.findall(r"\b\w+\b", text)
    data.word_count = len(words)

    # 10. Links extraction
    for a in soup.find_all("a", href=True):
        raw_href = a["href"].strip()
        anchor_text = a.get_text(strip=True)
        norm_url = normalize_url(raw_href, current_url)
        if not norm_url:
            continue

        if is_same_origin(norm_url, root_hostname):
            data.internal_links.append(
                {"href": norm_url, "text": anchor_text, "raw": raw_href}
            )
            data.discovered_internal_urls.add(norm_url)
        else:
            data.external_links.append(
                {"href": norm_url, "text": anchor_text, "raw": raw_href}
            )

    return data
