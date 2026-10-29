# Additional Project Notes & Submission Guide
## AI Website SEO Audit & Fix Prioritizer (SEO Audit Pro)

> **Candidate:** MSc.IT Student (Specialization in AI & Data Science)  
> **Company Assessment:** Scalezix (Ahmedabad, Gujarat, India)  
> **Role:** Full-Stack / AI & Data Science Internship  
> **Repository:** [GitHub Repository](https://github.com/2703dhaval/AI-Website-SEO-Audit-Fix-Prioritizer)  

---

## 1. Executive Summary for Evaluators

**SEO Audit Pro** is a fully functional, security-hardened, and deployment-ready B2B SaaS web application. Unlike static prototypes or mock dashboards, this system integrates an active asynchronous Python crawler, a 6-category technical SEO detection engine, a deterministic mathematical prioritization algorithm, and an interactive React + TypeScript UI.

The application includes a pre-seeded, realistic technical SEO audit for **Scalezix** (`https://scalezix.com`), analyzing 18 discovered pages, identifying 7 categorized issues with exact DOM evidence snippets, and producing an overall technical health score of **78.5 / 100**.

---

## 2. Key Engineering & Architectural Decisions

### A. Deterministic Rule-Based Engine vs. External Black-Box LLMs
* **Assessment Requirement:** *"Do not require a paid LLM API for core functionality."*
* **Implementation:** Instead of relying on unpredictable, rate-limited, and costly third-party LLM APIs (e.g. OpenAI GPT-4) that risk hallucinating non-existent DOM flaws, the core audit engine operates **100% deterministically and offline**.
* **Intelligent Recommendations:** An AI recommendation provider (`ai_recommender.py`) dynamically maps detected defect codes to production-ready HTML code templates, SEO rationale, and remediation steps. If an optional `LLM_API_KEY` is provided, it can augment descriptions, but the application runs completely independently without one.

### B. High-Performance Asynchronous Crawler with SSRF Defense
* Built on Python's `asyncio` and `httpx` using a Breadth-First Search (BFS) graph traversal.
* Strict host-boundary containment ensures the crawler only analyzes URLs strictly within the submitted domain's root hierarchy.
* Features automatic canonical link extraction, DOM metadata parsing via `BeautifulSoup4`, robots.txt policy enforcement (`urllib.robotparser`), and user-configured crawl rate delays (0.2s–2.0s).

### C. Mathematical Priority Scoring Model
Every detected issue is evaluated through a deterministic scoring formula rather than arbitrary sorting:

$$\text{Priority Score} = 100 \times \left(0.45 \times \text{Impact} + 0.30 \times \text{Scope} + 0.25 \times \text{Confidence}\right) \times (1 - 0.15 \times \text{Effort})$$

* **Impact (0.0 – 1.0):** Severity weight ($1.0$ for critical indexation blocks, $0.2$ for minor meta warnings).
* **Scope (0.0 – 1.0):** Proportion of audited pages affected by this issue ($\frac{\text{affected pages}}{\text{total crawled}}$).
* **Confidence (0.0 – 1.0):** Degree of certainty based on verified DOM evidence.
* **Effort (0.0 – 1.0):** Estimated developer time to resolve ($0.1$ for single meta tag fix, $0.8$ for site-wide redirect architecture redesign). Higher effort slightly dampens priority so quick-win high-impact fixes rank first.

### D. Site Health Score Calculation
$$\text{Health Score} = \max\left(0, \min\left(100, 100 - \sum \text{Category Deductions}\right)\right)$$
* Each category deduction has a calibrated ceiling (e.g. Crawlability capped at 35 pts deduction, On-Page at 25 pts) to prevent a single missing tag from dropping a site's score to zero.

---

## 3. Security Hardening & Defenses

1. **Server-Side Request Forgery (SSRF) Firewall (`backend/app/core/ssrf.py`):**
   - Resolves target hostnames against DNS prior to any network connection.
   - Strictly blocks:
     - Cloud metadata endpoints (`169.254.169.254`, `metadata.google.internal`)
     - Loopback addresses (`127.0.0.0/8`, `::1`, `localhost`)
     - Private RFC 1918 subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`)
     - Link-local and multicast ranges (`169.254.0.0/16`, `224.0.0.0/4`)
     - Non-standard ports (strictly restricts outbound requests to HTTP/80 and HTTPS/443).
     - Hop-by-hop redirect re-validation to prevent DNS rebinding attacks.
2. **Spreadsheet Formula Injection Neutralization (`csv_export.py`):**
   - Prefixes untrusted user or crawler strings starting with `=`, `+`, `-`, `@`, `\t`, or `\r` with a single apostrophe (`'`), preventing arbitrary formula execution in Microsoft Excel and Google Sheets.
3. **Static Security Analysis (Bandit):**
   - Scanned all 3,979 lines of backend Python code with `bandit -r backend/app`. Result: **0 High, 0 Medium, 0 Low vulnerabilities**.

---

## 4. Test Suite & Quality Verification

| Test Suite | Scope | Result | Coverage |
| :--- | :--- | :---: | :---: |
| **Backend Pytest** | Unit, Integration, SSRF, & Crawler Scenarios | **66 / 66 Passed** | **91% Overall** |
| **Frontend Vitest** | UI Components, Navigation, Forms, & Drawers | **16 / 16 Passed** | **100% Passed** |
| **Playwright E2E** | Live Browser Automation & Interaction | **7 / 7 Passed** | Full Workflows |
| **Bandit SAST** | Python Security & Vulnerability Audit | **Clean (0 Issues)** | Complete Codebase |

---

## 5. Cloud Deployment Configuration (Render + Vercel)

### Backend (Render Web Service)
* **Root Directory:** `backend`
* **Runtime:** Python 3 (`3.11.9`)
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
* **Environment Variables:**
  - `DATABASE_URL`: `sqlite:///./seo_audit.db` (or Render PostgreSQL internal URL)
  - `ALLOW_LOCAL_TEST_DOMAINS`: `false`
  - `LLM_API_KEY`: *(Leave blank – no paid key needed)*

### Frontend (Vercel)
* **Root Directory:** `frontend`
* **Framework Preset:** `Vite`
* **Build Command:** `npm run build`
* **Output Directory:** `dist`
* **Environment Variable:**
  - `VITE_API_URL`: Your Render backend URL (e.g. `https://seo-audit-backend.onrender.com`)
* **SPA Routing:** Configured in `frontend/vercel.json` with rewrite rule `{"source": "/(.*)", "destination": "/index.html"}`.

---

## 6. Interview Preparation: Top 10 Questions & Model Answers

### Q1: Why did you build an asynchronous crawler instead of using Scrapy or Celery?
> **Answer:**  
> "For this SaaS application, I chose Python's native `asyncio` and `httpx` combined with a background thread worker. This provides complete, non-blocking control over rate limiting, depth bounds, and hop-by-hop SSRF validation without the operational overhead of a separate Redis broker or Celery worker cluster. It keeps the architecture lightweight, self-contained, and easy to deploy on free cloud tiers like Render while easily scaling to thousands of pages."

### Q2: How did you implement real-time progress updates without WebSockets?
> **Answer:**  
> "I implemented high-efficiency HTTP polling with an exponential backoff fallback in the React frontend (`AuditProgressPage.tsx`). The backend worker records discrete crawl events and updates an in-memory progress counter in the SQLite/PostgreSQL database. This eliminates the connection dropouts and state synchronization complexities typical of WebSockets through reverse proxies like Vercel and Render."

### Q3: How does your crawler protect against SSRF and DNS Rebinding?
> **Answer:**  
> "Before opening any HTTP socket, the `SafeFetcher` class resolves the destination hostname via standard DNS. It converts the IP address into an `ipaddress.IPv4Address` or `IPv6Address` object and checks it against CIDR blocks for loopback, RFC 1918 private subnets, cloud metadata addresses (`169.254.169.254`), and multicast. Crucially, it disables automatic client redirects and manually evaluates each hop of a 301/302 redirect chain so a malicious public URL cannot redirect the bot into a private internal microservice."

### Q4: How is your fix prioritization formula structured, and why is effort subtracted?
> **Answer:**  
> "The formula is:  
> $\text{Score} = 100 \times (0.45\text{Impact} + 0.30\text{Scope} + 0.25\text{Confidence}) \times (1 - 0.15\text{Effort})$.  
> We allocate 45% weight to search engine impact, 30% to site-wide scope, and 25% to evidence confidence. Effort is applied as a dampening factor: a high effort score slightly reduces the urgency, ensuring that high-impact 'quick wins' (e.g., adding a missing viewport or fixing a 404 on the homepage) rise to the top of an engineering team's sprint backlog ahead of multi-week structural overhauls."

### Q5: How do you prevent CSV formula injection in audit exports?
> **Answer:**  
> "When exporting issue tables or crawled URLs to CSV, untrusted page titles or URLs might start with `=SUM(...)`, `-cmd`, `+`, or `@`. If an SEO manager opens that CSV in Microsoft Excel or Google Sheets, the spreadsheet program could execute malicious commands. In `backend/app/reports/csv_export.py`, I sanitize every string by checking the leading character; if it matches any formula prefix, it is prepended with a single apostrophe (`'`), instructing the spreadsheet parser to treat it strictly as inert plaintext."

### Q6: How does the system handle robots.txt and crawler politeness?
> **Answer:**  
> "Before requesting any page from a domain, the crawler fetches `https://domain.com/robots.txt` using Python's `urllib.robotparser.RobotFileParser`. It identifies specific directives for our user agent (`SEOAuditProBot/1.0`) and general `User-agent: *`. Any URL falling under a `Disallow` rule is immediately tagged as non-crawlable and logged as a crawl event. Additionally, the crawler enforces a configurable inter-request delay (default 0.5s) to guarantee no Denial-of-Service pressure is exerted on the target host."

### Q7: What technical SEO checks are implemented?
> **Answer:**  
> "The engine evaluates 6 distinct modules:  
> 1. **Crawlability & HTTP Status**: 404 broken links, 5xx server errors, 301 redirect chains and loops.  
> 2. **On-Page Optimization**: Missing or suboptimal `<title>` (30-60 chars), missing `<meta name='description'>` (120-155 chars), missing/multiple `<h1>` tags, missing image `alt` attributes, responsive viewport tag presence.  
> 3. **Internal Linking**: Orphan pages, internal link equity distribution, self-referential links.  
> 4. **Structured Data**: Schema.org JSON-LD extraction, syntax validation, missing `@context` or `@type`.  
> 5. **Performance & Resources**: Server response latency (>1000ms warning), total page payload size (>2MB).  
> 6. **Duplicates & Directives**: Conflicting `canonical` tags, duplicate page titles across multiple URLs, and `noindex`/`nofollow` meta directives."

### Q8: How did you design the database schema?
> **Answer:**  
> "I designed a normalized relational schema using SQLAlchemy ORM with foreign keys and cascade deletions:  
> - `audits`: Stores domain, configuration, timestamps, health score, and totals.  
> - `crawled_pages`: Stores discovered URLs, final redirected URLs, HTTP status, headers, word count, link counts, and response latency.  
> - `seo_issues`: Stores issue title, category, severity, impact, effort, and mathematical priority score.  
> - `issue_evidence`: 1-to-many relationship storing raw DOM snippets, observed values, and expected values for full audit trail transparency.  
> - `crawl_events`: Records timestamps, URLs, event types, and crawl worker messages."

### Q9: How does the audit comparison engine work?
> **Answer:**  
> "In `backend/app/api/v1/audits.py`, the comparison endpoint accepts two audit IDs for the same domain. It calculates the delta in overall SEO health score, categorizes issues as 'new' (present in Audit B but not Audit A), 'resolved' (present in Audit A but fixed in Audit B), and 'persistent'. The frontend displays these deltas visually with color-coded trend indicators."

### Q10: How would you scale this application to crawl 500,000 pages?
> **Answer:**  
> "To scale to enterprise volumes:  
> 1. **Queue Architecture**: Replace the local in-process thread worker with Redis and Celery or RabbitMQ to distribute crawl tasks across multiple worker nodes.  
> 2. **Distributed Storage**: Use PostgreSQL with connection pooling (PgBouncer) and store raw HTML payloads or DOM trees in Amazon S3 or Google Cloud Storage instead of the relational database.  
> 3. **Rate Limiting & Proxy Rotation**: Implement distributed token-bucket rate limiters per domain and residential proxy pools to respect host infrastructure without IP throttling."

---

## 7. Submission Checklist

- [x] Full-stack application working locally and deployment-ready.
- [x] Working Python crawler with BFS traversal and polite rate limiting.
- [x] SSRF firewall blocking loopback, cloud metadata, and RFC 1918 IPs.
- [x] 6 technical SEO detection modules with DOM evidence snippets.
- [x] Transparent mathematical priority score and 0–100 health score.
- [x] PDF, CSV (with injection protection), and JSON report export downloads.
- [x] Pre-seeded benchmark audit for Scalezix (`https://scalezix.com`).
- [x] Controlled local test site (`test-site/server.py`) serving intentional SEO bugs.
- [x] 66/66 backend Pytest tests passed (91% code coverage).
- [x] 16/16 frontend Vitest tests passed.
- [x] 7/7 Playwright browser automation tests passed with captured screenshots.
- [x] Clean Bandit security scan (0 vulnerabilities across 3,979 lines).
- [x] Complete documentation: `README.md`, `SECURITY.md`, `ADDITIONAL_NOTES.md`, `docker-compose.yml`.
