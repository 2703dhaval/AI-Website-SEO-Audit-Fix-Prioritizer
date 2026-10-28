"""
Local Test Website for SEO Audit Pro
Serves intentional SEO conditions for unit, integration, and end-to-end testing.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import socket


PAGES = {
    "/": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Test Site - Main Home Hub</title>
    <meta name="description" content="A comprehensive test website used to rigorously benchmark technical SEO crawler detection rules.">
    <link rel="canonical" href="http://127.0.0.1:8765/">
</head>
<body>
    <h1>SEO Test Site Home</h1>
    <p>Welcome to the controlled local test website. Explore our test scenarios below:</p>
    <ul>
        <li><a href="/optimized">Well-Optimized Page (Benchmark)</a></li>
        <li><a href="/missing-title">Page Missing Title</a></li>
        <li><a href="/missing-meta-desc">Page Missing Meta Description</a></li>
        <li><a href="/duplicate-title-1">Duplicate Title Page A</a></li>
        <li><a href="/duplicate-title-2">Duplicate Title Page B</a></li>
        <li><a href="/missing-h1">Page Missing H1</a></li>
        <li><a href="/missing-alt">Page with Missing Image Alt</a></li>
        <li><a href="/broken-link">Broken Internal Link (404)</a></li>
        <li><a href="/redirect-me">Redirecting Page (301)</a></li>
        <li><a href="/noindex-page">Noindex Page</a></li>
        <li><a href="/canonical-mismatch">Canonical Mismatch Page</a></li>
        <li><a href="/slow-page">Slow Page</a></li>
        <li><a href="/disallowed-by-robots">Disallowed by Robots</a></li>
    </ul>
</body>
</html>""",

    "/optimized": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Perfect Page - Fully Optimized Technical SEO</title>
    <meta name="description" content="This page meets all technical SEO requirements including valid title, description, schema markup, and images.">
    <link rel="canonical" href="http://127.0.0.1:8765/optimized">
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": "Perfect Page",
        "description": "Example of fully valid structured data."
    }
    </script>
</head>
<body>
    <h1>Optimized Benchmark Page</h1>
    <h2>Section 1: Content Quality</h2>
    <p>This page contains more than two hundred and fifty words of genuine, high quality informative text explaining technical SEO. Search engines evaluate depth of topical coverage, mobile responsiveness, semantic hierarchy, and structured metadata. By adhering to these standards, websites establish high relevance for their intended search queries.</p>
    <img src="/static/chart.png" alt="Informative performance chart" width="400" height="200">
    <h2>Section 2: Navigation</h2>
    <p>Back to the <a href="/">homepage</a>.</p>
</body>
</html>""",

    "/missing-title": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Title is missing -->
    <meta name="description" content="This page is intentionally missing a title element.">
</head>
<body>
    <h1>Page With Missing Title</h1>
    <p>Testing detection of absent title tags. <a href="/">Return home</a>.</p>
</body>
</html>""",

    "/missing-meta-desc": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Missing Meta Description - Test Scenario</title>
</head>
<body>
    <h1>Page Missing Meta Description</h1>
    <p>Testing detection of omitted meta description tags. <a href="/">Return home</a>.</p>
</body>
</html>""",

    "/duplicate-title-1": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Identical Duplicate Title Across Pages</title>
    <meta name="description" content="First page with a duplicate title.">
</head>
<body>
    <h1>Duplicate Title Scenario Page 1</h1>
    <p>Testing duplicate title tags across multiple URLs. <a href="/">Home</a>.</p>
</body>
</html>""",

    "/duplicate-title-2": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Identical Duplicate Title Across Pages</title>
    <meta name="description" content="Second page with a duplicate title.">
</head>
<body>
    <h1>Duplicate Title Scenario Page 2</h1>
    <p>Testing duplicate title tags across multiple URLs. <a href="/">Home</a>.</p>
</body>
</html>""",

    "/missing-h1": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Missing Primary H1 Heading - Test Scenario</title>
    <meta name="description" content="This page skips H1 and starts directly with H2.">
</head>
<body>
    <h2>Subheading Without Preceding H1</h2>
    <p>Testing missing H1 detection. <a href="/">Return home</a>.</p>
</body>
</html>""",

    "/missing-alt": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page with Images Missing Alt Attributes</title>
    <meta name="description" content="This page contains images missing alt text attributes.">
</head>
<body>
    <h1>Images Without Alt Attributes</h1>
    <img src="/test-photo.jpg">
    <img src="/hero-banner.png">
    <p><a href="/">Return home</a>.</p>
</body>
</html>""",

    "/noindex-page": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Noindex Directive Page - Test Scenario</title>
    <meta name="robots" content="noindex, follow">
    <meta name="description" content="This page has an explicit noindex directive in its robots meta tag.">
</head>
<body>
    <h1>Noindex Directive Page</h1>
    <p>This page should be identified as non-indexable due to meta robots directive. <a href="/">Home</a>.</p>
</body>
</html>""",

    "/canonical-mismatch": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Canonical Mismatch Test Page</title>
    <meta name="description" content="This page specifies a canonical URL pointing to an entirely different URL.">
    <link rel="canonical" href="http://127.0.0.1:8765/optimized">
</head>
<body>
    <h1>Canonical Mismatch Page</h1>
    <p>Canonical tag points away to /optimized. <a href="/">Home</a>.</p>
</body>
</html>""",

    "/robots.txt": """User-agent: *
Disallow: /disallowed-by-robots
Sitemap: http://127.0.0.1:8765/sitemap.xml
""",

    "/sitemap.xml": """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>http://127.0.0.1:8765/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>http://127.0.0.1:8765/optimized</loc>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
</urlset>""",

    "/disallowed-by-robots": """<!DOCTYPE html>
<html>
<head><title>Disallowed by Robots</title></head>
<body><h1>This section is disallowed in robots.txt</h1></body>
</html>"""
}


class SEOTestServerHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress console spam during automated tests

    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/redirect-me":
            self.send_response(301)
            self.send_header("Location", "/optimized")
            self.end_headers()
            return

        if path == "/broken-link":
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>404 Not Found</h1><p>Test broken page</p>")
            return

        if path in PAGES:
            content = PAGES[path]
            content_type = "text/xml" if path.endswith(".xml") else ("text/plain" if path.endswith(".txt") else "text/html; charset=utf-8")
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
            return

        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"404 Not Found")


def run_test_server(port: int = 8765):
    server = HTTPServer(("127.0.0.1", port), SEOTestServerHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    return server


if __name__ == "__main__":
    print("Starting SEO Local Test Site on http://127.0.0.1:8765 ...")
    srv = run_test_server(8765)
    print("Serving pages. Press Ctrl+C to terminate.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        srv.shutdown()
