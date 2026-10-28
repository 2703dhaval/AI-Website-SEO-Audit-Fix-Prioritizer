# Security Policy & Architecture

## Threat Model Overview

**SEO Audit Pro** accepts arbitrary user-submitted URLs to perform web crawling and technical SEO analysis. This architecture introduces specific security risks that must be defended systematically:

1. **Server-Side Request Forgery (SSRF)**: Attackers attempting to leverage the crawler to scan internal networks, reach loopback administrative ports (e.g. `127.0.0.1:8000`), or exfiltrate cloud credentials via instance metadata endpoints (e.g., `169.254.169.254`).
2. **CSV / Spreadsheet Formula Injection**: Malicious HTML metadata containing formula triggers (`=`, `+`, `-`, `@`) executing arbitrary code when reports are opened in Microsoft Excel or Google Sheets.
3. **Cross-Site Scripting (XSS)**: Untrusted crawled web page titles, snippets, or script content rendered unsafely in browser sessions.
4. **Denial of Service & Resource Exhaustion (DoS)**: Giga-byte HTML downloads, infinite redirect loops, deep directory bombs, or rapid concurrent crawls exhausting server memory.

---

## Security Protections Implemented

### 1. SSRF Firewall (`app/core/ssrf.py`)
- **Scheme Enforcement**: Permits only `http` and `https`. Schemes like `file://`, `gopher://`, `ftp://`, `data:`, and `javascript:` are rejected outright.
- **Embedded Credentials Blocked**: Reject URLs containing username or password tokens (`http://user:pass@domain`).
- **Loopback & Private Network Firewall**: Pre-resolves DNS and checks the resulting IP against the following blocked CIDR blocks:
  - Loopback (`127.0.0.0/8`, `::1/128`)
  - RFC 1918 Private IPv4 (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`)
  - Link-Local & Cloud Metadata (`169.254.0.0/16`, `fe80::/10`)
  - Documentation, Multicast, Broadcast (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`, `224.0.0.0/4`, `255.255.255.255/32`)
  - Disallowed Hostnames (`metadata.google.internal`, `metadata.goog`, `instance-data`)
- **Hop-by-Hop Redirect Re-Validation**: The crawler disables automatic HTTP redirect following. Every `Location` header is individually parsed, joined, and re-submitted to the SSRF validator before following.
- **Port Restrictions**: Blocks non-standard ports (such as SSH `22`, SMTP `25`, MySQL `3306`, PostgreSQL `5432`, Redis `6379`, MongoDB `27017`).

### 2. Spreadsheet Formula Injection Protection (`app/reports/csv_export.py`)
- Any CSV cell value originating from untrusted web pages that begins with formula initiation characters (`=`, `+`, `-`, `@`, `\t`, `\r`) is sanitized by prepending a single quote (`'`), neutralizing dynamic formula execution in Excel and LibreOffice Calc.

### 3. XML Entity & PDF Escaping (`app/reports/pdf_generator.py`)
- All titles, descriptions, and code snippets rendered in ReportLab PDF generation are escaped using `html.escape()`, preventing XML parsing errors or unclosed entity injections.

### 4. Resource & Concurrency Caps (`app/crawler/fetcher.py`)
- **Response Size Ceiling**: Responses exceeding 5 MB (`MAX_RESPONSE_BYTES`) are terminated immediately to prevent memory exhaustion.
- **Redirect Chain Limit**: Maximum 5 hops enforced; redirect loops are detected and halted.
- **Timeouts**: 10-second hard request timeout on all network sockets.
- **Rate-Limiting Crawl Delay**: Enforces a configurable delay between requests per domain (default 0.5s), respecting robots.txt crawl-delay directives.

### 5. Database & API Security
- SQLAlchemy ORM parameterization used exclusively; no raw concatenated SQL.
- Hardcoded secrets and stack traces are suppressed in production responses via the global exception handler in `app/main.py`.
- HTTP Security Headers enabled:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`

---

## Static Security Analysis Verification

Static security analysis was conducted using **Bandit**:
```
Run metrics:
	Total issues (by severity):
		Undefined: 0
		Low: 0
		Medium: 0
		High: 0
Files scanned: 41
Lines of code: 3,979
```
Zero high, medium, or low security defects identified.

---

## Residual Risks & Production Infrastructure Recommendations

Application-level SSRF defenses significantly mitigate attack vectors, but cannot completely eliminate DNS rebinding if an attacker controls a public nameserver that alternates between a valid IP and an internal IP. For hardened enterprise deployments:
1. **Network Egress Filtering**: Deploy workers in an isolated VPC subnet without routes to internal management networks.
2. **Dedicated Outbound Proxy**: Route crawler traffic through a forward proxy (such as Squid or Smokescreen) that enforces egress IP restrictions at the kernel/socket layer.
