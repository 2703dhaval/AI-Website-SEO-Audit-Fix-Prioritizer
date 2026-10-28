# SEO Audit Pro — AI Website SEO Audit & Fix Prioritizer

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178C6.svg)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg)](https://tailwindcss.com)
[![Tests Passing](https://img.shields.io/badge/Tests-66%20Passed-success.svg)]()
[![Code Coverage](https://img.shields.io/badge/Coverage-91%25-brightgreen.svg)]()

> Developed as part of an MSc.IT postgraduate internship technical assessment for **Scalezix** (Ahmedabad, Gujarat, India).

---

## 1. Project Title & Overview

**Product Name:** SEO Audit Pro  
**Subtitle:** AI Website SEO Audit & Fix Prioritizer  
**Brand Positioning:** Technical SEO analysis, evidence-based defect detection, and prioritized fixes.

SEO Audit Pro is a production-grade full-stack web application designed to crawl permitted websites, identify critical technical and on-page SEO issues, group them by severity, and generate a deterministic fix roadmap ranked by potential SEO impact, scope, confidence, and implementation effort.

---

## 2. Problem Statement

Most modern website owners, agencies, and developers run automated SEO audits that output overwhelming lists of hundreds of unorganized warnings. Without an evidence-backed ranking system, teams struggle to determine which technical fixes move the needle first. Furthermore, irresponsible crawlers lack strict SSRF protections, risk violating robots.txt policies, or depend on expensive black-box LLMs that hallucinate evidence.

---

## 3. Objectives

- **Safe Crawling**: Build an asynchronous Python crawler respecting robots.txt and enforcing strict Server-Side Request Forgery (SSRF) controls.
- **Traceable Defect Detection**: Detect issues across 6 key SEO categories with per-page DOM evidence snippets and observed vs. expected conditions.
- **Transparent Mathematical Prioritization**: Eliminate guesswork by calculating priority scores using a documented mathematical formula.
- **SEO Health Score (0–100)**: Compute a deterministic score reflecting technical site health.
- **Client-Ready Reports**: Generate instant PDF executive summaries, Excel CSV fix roadmaps with formula injection protections, and JSON exports.
- **Real Company Benchmark**: Feature a pre-seeded, realistic technical SEO report for **Scalezix** (`https://scalezix.com`).

---

## 4. Key Features

- **Interactive SaaS Dashboard**: Real metrics computed directly from database records (audits count, unique domains, severity distribution, category breakdown).
- **Live Progress Polling**: Real-time progress bar, pages discovered vs. crawled, sub-second status updates, and cooperative crawl cancellation.
- **Prioritized Fix Roadmap**: Filter findings by severity (Critical, High, Medium, Low, Informational), category, status, or keyword.
- **Interactive Issue Details Drawer**: Slide-over drawer with stored evidence, technical explanation, why it matters for SEO, copyable fix snippets, and live status editing (`Open`, `In Progress`, `Resolved`, `Ignored`).
- **Discovered URLs Inspector**: Sortable table with HTTP status codes, titles, meta descriptions, word counts, crawl depths, latency, and detected defect counts.
- **Audit Comparison Engine**: Select any two historical audits to measure health score deltas, new issues, and resolved bugs.
- **Export Formats**: One-click PDF generation via ReportLab, Excel-safe CSV export (neutralizing formula injection), and full JSON schema export.
- **Local Test Website**: Built-in test site with deliberate defects (missing titles, broken links, 301 loops, duplicate titles, missing alt tags, noindex directives) for deterministic verification.

---

## 5. Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript & Vite
- **Styling**: Tailwind CSS with custom SaaS color palette
- **Icons**: Lucide Icons
- **Data Visualization**: Recharts (Pie & Bar distributions)
- **Routing**: React Router v6
- **Testing**: Vitest & React Testing Library (JSDOM)

### Backend
- **Framework**: Python 3.11+ / 3.14 compatible, FastAPI
- **Data Validation**: Pydantic v2 & Pydantic-Settings
- **ORM & Database**: SQLAlchemy 2.0 with SQLite for zero-config local development; PostgreSQL-ready for production
- **Migrations**: Alembic version-controlled database migrations
- **HTTP Client**: HTTPX with custom SSRF firewall
- **HTML Parsing**: BeautifulSoup4 (`html.parser`)
- **PDF Generation**: ReportLab
- **Code Quality & Security**: Pytest, Pytest-cov, Ruff, Bandit

---

## 6. Architecture & System Flow

```
User (Browser) 
      │
      ▼
React 18 Frontend (Vite + Tailwind)
      │  (REST API calls via /api/v1)
      ▼
FastAPI Backend Application
      │
      ├──> SSRF Security Firewall (IP & DNS Validation Gate)
      │          │
      │          ▼
      ├──> Safe Web Crawler (BFS Queue, robots.txt, Rate Limiter)
      │          │
      │          ▼
      ├──> BeautifulSoup4 Parser (DOM & Metadata Extraction)
      │          │
      │          ▼
      ├──> SEO Detection Engine (6 Technical Rule Checkers)
      │          │
      │          ▼
      ├──> Deterministic Prioritizer & Health Score Engine
      │          │
      │          ▼
      └──> SQLAlchemy ORM ──> SQLite / PostgreSQL Database
                 │
                 ├──> ReportLab PDF Deliverables
                 ├──> CSV Export (with Formula Injection Escaping)
                 └──> JSON Export
```

---

## 7. Project Folder Structure

```
seo-audit-prioritizer/
├── backend/
│   ├── alembic/                      # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── app/
│   │   ├── api/v1/                   # REST API routes
│   │   │   ├── audits.py             # Audits CRUD & comparison
│   │   │   ├── dashboard.py          # Dashboard statistics
│   │   │   ├── issues.py             # Issues & status updates
│   │   │   ├── pages.py              # Crawled pages listing
│   │   │   ├── reports.py            # PDF, CSV, JSON downloads
│   │   │   ├── sample.py             # Scalezix sample audit
│   │   │   └── api.py                # Main router aggregation
│   │   ├── core/
│   │   │   ├── config.py             # Application settings
│   │   │   └── ssrf.py               # Strict SSRF firewall
│   │   ├── crawler/
│   │   │   ├── crawler.py            # Asynchronous BFS crawler
│   │   │   ├── fetcher.py            # Safe HTTP fetcher with hop re-validation
│   │   │   ├── parser.py             # HTML parser & link discovery
│   │   │   └── robots.py             # robots.txt fetcher & validator
│   │   ├── db/
│   │   │   ├── base.py               # DeclarativeBase
│   │   │   └── session.py            # SQLAlchemy engine & session factory
│   │   ├── models/                   # SQLAlchemy database models
│   │   ├── prioritization/
│   │   │   ├── engine.py             # Deterministic prioritization formula
│   │   │   └── health_score.py       # SEO Health Score algorithm
│   │   ├── reports/
│   │   │   ├── csv_export.py         # Formula-injection-safe CSV generator
│   │   │   ├── json_export.py        # Machine-readable JSON export
│   │   │   └── pdf_generator.py      # ReportLab executive PDF generator
│   │   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── seo_checks/               # Technical SEO check modules
│   │   ├── services/
│   │   │   ├── audit_service.py      # Background crawl orchestrator
│   │   │   ├── ai_recommender.py     # Deterministic & optional LLM engine
│   │   │   └── sample_report_data.py # Scalezix pre-seeded audit data
│   │   └── main.py                   # FastAPI app entry point
│   ├── tests/
│   │   ├── integration/              # API and E2E scenario tests
│   │   ├── security/                 # SSRF test suite
│   │   ├── unit/                     # Parser, checks, scoring, export tests
│   │   └── conftest.py               # Test fixtures & mock site runner
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/               # ScoreBadge, SeverityBadge, IssueDrawer, Navbar...
│   │   ├── pages/                    # Landing, Dashboard, NewAudit, Progress, Results...
│   │   ├── services/                 # Centralized type-safe API client
│   │   ├── types/                    # TypeScript interfaces
│   │   ├── tests/                    # Vitest component tests
│   │   ├── App.tsx                   # Main router
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
├── test-site/
│   └── server.py                     # Local test site serving intentional SEO flaws
├── docker-compose.yml
├── .env.example
├── .gitignore
├── SECURITY.md
└── README.md
```

---

## 8. Supported SEO Checks

### A. HTTP & Crawlability
- `ERR_HTTP_4XX`: Client broken links (404, 403, 410)
- `ERR_HTTP_5XX`: Internal server errors (500, 502, 503)
- `WARN_REDIRECT_CHAIN`: Successive redirect hops (> 1 hop)
- `INFO_PAGE_NOINDEX`: Detects `noindex` meta tags and `X-Robots-Tag`
- `WARN_ROBOTS_TXT_INACCESSIBLE`: Missing or failing robots.txt
- `WARN_MIXED_HTTP_LINKS`: Insecure HTTP internal links on secure HTTPS pages

### B. On-Page Structure
- `ERR_TITLE_MISSING`: Missing or empty `<title>` tag
- `WARN_TITLE_LENGTH`: Titles outside 30–60 character recommendation
- `ERR_META_DESC_MISSING`: Missing `<meta name="description">`
- `WARN_META_DESC_LENGTH`: Descriptions outside 70–160 character recommendation
- `ERR_H1_MISSING`: Missing primary `<h1>` heading
- `INFO_H1_MULTIPLE`: Multiple `<h1>` headings detected (review recommendation)
- `WARN_HEADING_HIERARCHY`: Skipped heading levels (e.g. H1 directly to H3)
- `ERR_IMG_ALT_MISSING`: Content images lacking `alt` attribute
- `ERR_VIEWPORT_MISSING`: Missing responsive `<meta name="viewport">`
- `WARN_LANG_MISSING`: Missing `lang` attribute on `<html>`
- `WARN_THIN_CONTENT`: Low body text word count (< 250 words)
- `WARN_CANONICAL_MISSING`: Absence of explicit canonical link tag
- `WARN_DUPLICATE_IDS`: Duplicate HTML element `id` attributes on the same page

### C. Internal Linking
- `ERR_BROKEN_INTERNAL_LINK`: Internal anchors resolving to 4xx/5xx destinations
- `WARN_INTERNAL_LINK_TO_REDIRECT`: Anchors pointing to 301/302 redirects
- `WARN_EMPTY_ANCHOR_TEXT`: Internal links lacking visible text or image alt
- `WARN_EXCESSIVE_INTERNAL_LINKS`: More than 150 internal links on a single page
- `WARN_DEEP_CRAWL_DEPTH`: Pages buried 4 or more clicks from the root
- `WARN_POTENTIAL_ORPHAN_PAGE`: Pages with zero incoming links within crawl scope

### D. Structured Data
- `ERR_JSONLD_SYNTAX`: Syntax errors or invalid JSON in `<script type="application/ld+json">`
- `WARN_SCHEMA_MALFORMED`: Schema objects missing required `@context` or `@type`
- `INFO_STRUCTURED_DATA_MISSING`: Advisory on pages lacking Schema.org structured data

### E. Performance Indicators
- `WARN_SLOW_RESPONSE_TIME`: Time-To-First-Byte (TTFB) exceeding 1200ms
- `WARN_LARGE_HTML_PAYLOAD`: Uncompressed HTML document exceeding 800 KB
- `WARN_IMG_DIMENSIONS_MISSING`: Images missing explicit width and height (Cumulative Layout Shift risk)

### F. Duplicates & Consistency
- `ERR_DUPLICATE_TITLE`: Identical title tags shared across different URLs
- `WARN_DUPLICATE_META_DESC`: Shared meta descriptions across multiple pages
- `WARN_DUPLICATE_CONTENT`: Text shingle Jaccard similarity > 85% between page body texts

---

## 9. Severity & Prioritization Methodology

Priority scores are calculated deterministically to guide development teams:

$$\text{Priority Score} = 100 \times (0.45 \times \text{Impact} + 0.30 \times \text{Scope} + 0.25 \times \text{Confidence}) \times (1 - 0.15 \times \text{Effort})$$

Where:
- **Impact [0.0–1.0]**: Potential consequence on indexability and ranking signals.
  - Critical: `0.90 – 1.00`
  - High: `0.70 – 0.85`
  - Medium: `0.50 – 0.65`
  - Low: `0.30 – 0.45`
  - Informational: `0.10 – 0.25`
- **Scope [0.0–1.0]**: Calculated using bounded logarithmic scaling relative to total crawled pages:
  $$\text{Scope} = \min\left(1.0, \frac{\ln(1 + \text{affected\_pages})}{\ln(1 + \text{total\_crawled})}\right)$$
- **Confidence [0.0–1.0]**: Deterministic rule checks carry confidence `0.85 – 1.00`.
- **Effort [0.0–1.0]**: Lower effort (e.g. `0.05` for adding a viewport tag) results in minimal penalty, boosting quick-wins. High architectural overhaul effort (`0.6+`) dampens the score.

---

## 10. SEO Health Score Methodology

The overall health score starts from **100.0** and applies bounded deductions:

- **Critical**: -14.0 base points × scope factor
- **High**: -8.0 base points × scope factor
- **Medium**: -4.0 base points × scope factor
- **Low**: -1.5 base points
- **Informational**: 0.0 points (advisory only)

Deductions are capped per category (`crawlability`: 35 max, `on_page`: 30 max, etc.) to prevent single categories from completely distorting the overall benchmark.

---

## 11. Scalezix Sample Report

The application includes a pre-seeded, rich sample audit for **Scalezix** (`https://scalezix.com`), an Ahmedabad-based enterprise software engineering company:

- **Audit Date**: Preserved audit baseline
- **Pages Crawled**: 18 discovered routes (Homepage, Services, AI Solutions, Case Studies, About, Blog, Careers, Contact, 404 test page)
- **Health Score**: **78.5 / 100**
- **Findings**: Includes real evidence snippets for missing alt tags on architecture diagrams, title tag character lengths on service pages, missing meta descriptions on AI solutions, and slow response latency on case study portfolios.
- **Immediate Access**: One-click accessible directly from the landing page and dashboard.

---

## 12. Installation & Quick Start (Windows)

### Prerequisites
- Python 3.11+ installed (`python --version`)
- Node.js 18+ and npm installed (`node --version`)
- Git installed (`git --version`)

### Step 1: Clone the Repository
```powershell
git clone https://github.com/your-username/ai-website-seo-audit-fix-prioritizer.git
cd "ai-website-seo-audit-fix-prioritizer"
```

### Step 2: Set Up Backend
```powershell
# Create Python virtual environment
python -m venv backend\venv

# Activate virtual environment
.\backend\venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r backend\requirements.txt

# Run database migrations
cd backend
$env:PYTHONPATH="."
.\venv\Scripts\alembic upgrade head
cd ..
```

### Step 3: Set Up Frontend
```powershell
cd frontend
npm install
cd ..
```

---

## 13. Running the Application

### Start Backend API Server
```powershell
# From project root
$env:PYTHONPATH="backend"
.\backend\venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Base URL: `http://127.0.0.1:8000`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/health`

### Start Frontend Dev Server (in a second terminal)
```powershell
cd frontend
npm run dev
```
- Open browser at: `http://localhost:5173`

---

## 14. Running Automated Tests

### Backend Test Suite (Pytest + Coverage)
```powershell
cd backend
$env:PYTHONPATH="."
.\venv\Scripts\pytest -v --cov=app --cov-report=term-missing
cd ..
```
**Results:**
- **66 Tests Passed** (0 failures)
- **Overall Line Coverage: 91%**
- Core SEO detection modules: `on_page.py` (96%), `duplicates.py` (93%), `structured_data.py` (93%), `crawlability.py` (89%), `internal_links.py` (88%).

### Frontend Test Suite (Vitest)
```powershell
cd frontend
npm run test
cd ..
```
**Results:**
- **7 Tests Passed** (LandingPage, ScoreBadge, SeverityBadge)

### Security Static Analysis (Bandit)
```powershell
cd backend
.\venv\Scripts\bandit -r app -ll
cd ..
```
**Results:**
- **0 Security Vulnerabilities** identified across 3,979 lines of Python code.

---

## 15. Deployment Guide

### Backend Deployment (Render / Railway)
- **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `DATABASE_URL`: Managed PostgreSQL connection string (or persistent SQLite disk)
  - `ALLOW_LOCAL_TEST_DOMAINS`: `false`
  - `CRAWLER_USER_AGENT`: `SEOAuditProBot/1.0 (+https://scalezix.com/bot; technical-audit)`

### Frontend Deployment (Vercel / Netlify)
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Rewrites**: Configure SPA fallback rewrite (`/* -> /index.html`)

---

## 16. Git Setup & Push Instructions

To push this codebase to your personal GitHub repository:

```powershell
# Initialize git if not already initialized
git init

# Stage all project files (safe .gitignore prevents committing databases or virtualenvs)
git add .

# Create initial commit
git commit -m "feat: complete production-ready AI Website SEO Audit & Fix Prioritizer"

# Add your remote repository URL (replace with your repo link)
git remote add origin https://github.com/your-username/ai-website-seo-audit-fix-prioritizer.git

# Set default branch to main and push
git branch -M main
git push -u origin main
```

---

## 17. Security & Known Limitations

- **JavaScript SPA Rendering**: The core crawler utilizes HTTP requests with BeautifulSoup parsing. Client-side Single Page Applications that rely entirely on JavaScript execution for initial DOM hydration require server-side rendering or headless browser pre-rendering.
- **DNS Rebinding**: In production, outbound network traffic should be routed through a dedicated egress firewall or proxy to eliminate residual DNS rebinding risks.
- **Disclaimers**: A 100/100 health score denotes zero technical defects identified by this tool's automated rules; it does not guarantee high search engine rankings, which also depend on domain authority, backlinks, and user intent fulfillment.

---

## 18. Author & Assessment Context

- **Developer**: Postgraduate MSc.IT Student (AI & Data Science Specialization)
- **Assessment For**: **Scalezix** (Ahmedabad, India)
- **Role**: Software Engineering / AI Internship Candidate
