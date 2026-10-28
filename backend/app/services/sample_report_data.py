import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.audit import Audit
from app.models.crawl_event import CrawlEvent
from app.models.crawled_page import CrawledPage
from app.models.issue import IssueEvidence, SEOIssue

SAMPLE_AUDIT_ID = "scalezix-sample-audit-001"


def seed_sample_company_audit(db: Session) -> Audit:
    """
    Creates or returns a comprehensive sample technical SEO audit
    for Scalezix (https://scalezix.com).
    """
    existing = db.query(Audit).filter(Audit.id == SAMPLE_AUDIT_ID).first()
    if existing:
        return existing

    now = datetime.now(UTC)
    started = now - timedelta(minutes=8)
    completed = now - timedelta(minutes=5)

    # 1. Audit Header
    sample_audit = Audit(
        id=SAMPLE_AUDIT_ID,
        audit_name="Scalezix Official Website Audit (Sample Report)",
        submitted_url="https://scalezix.com",
        normalized_domain="scalezix.com",
        status="completed",
        configuration={
            "max_pages": 25,
            "max_depth": 3,
            "crawl_delay": 0.5,
            "user_agent": "SEOAuditProBot/1.0",
        },
        started_at=started,
        completed_at=completed,
        error_summary=None,
        total_discovered_pages=18,
        total_crawled_pages=18,
        seo_health_score=78.5,
        scoring_version="v1.0",
        crawl_policy_summary="robots.txt accessed successfully (HTTP 200). Disallow: /admin, /api. Crawl-delay: none specified. 2 sitemaps identified.",
    )
    db.add(sample_audit)
    db.flush()

    # 2. Crawled Pages
    pages_data = [
        {
            "id": "scalezix-p-01",
            "requested_url": "https://scalezix.com",
            "final_url": "https://scalezix.com/",
            "canonical_url": "https://scalezix.com/",
            "http_status": 200,
            "title": "Scalezix - Driving Exponential Business Growth with Scalable Tech & AI",
            "meta_description": "Scalezix delivers cutting-edge software solutions, AI systems, and technology consulting to help modern businesses scale seamlessly.",
            "h1_data": [
                "Empowering Enterprises with Intelligent Technology Solutions",
                "Our Core Philosophy",
            ],
            "language": "en",
            "robots_directives": "index, follow",
            "word_count": 840,
            "internal_link_count": 42,
            "external_link_count": 6,
            "response_time_ms": 320.5,
            "response_size_bytes": 45200,
            "crawl_depth": 0,
            "indexability_status": "indexable",
        },
        {
            "id": "scalezix-p-02",
            "requested_url": "https://scalezix.com/services",
            "final_url": "https://scalezix.com/services",
            "canonical_url": "https://scalezix.com/services",
            "http_status": 200,
            "title": "Services | Scalezix Software Engineering, AI & Cloud Infrastructure Consulting Services",
            "meta_description": "Explore our full suite of enterprise engineering services including AI development, data pipelines, cloud migration, and custom software.",
            "h1_data": ["Transformative Technology Services"],
            "language": "en",
            "robots_directives": "index, follow",
            "word_count": 1250,
            "internal_link_count": 38,
            "external_link_count": 3,
            "response_time_ms": 410.0,
            "response_size_bytes": 52100,
            "crawl_depth": 1,
            "indexability_status": "indexable",
        },
        {
            "id": "scalezix-p-03",
            "requested_url": "https://scalezix.com/ai-solutions",
            "final_url": "https://scalezix.com/ai-solutions",
            "canonical_url": "https://scalezix.com/ai-solutions",
            "http_status": 200,
            "title": "AI & Data Solutions - Scalezix",
            "meta_description": "",  # Missing meta description
            "h1_data": ["Enterprise Artificial Intelligence & Machine Learning"],
            "language": "en",
            "robots_directives": "index, follow",
            "word_count": 910,
            "internal_link_count": 29,
            "external_link_count": 2,
            "response_time_ms": 380.2,
            "response_size_bytes": 41800,
            "crawl_depth": 2,
            "indexability_status": "indexable",
        },
        {
            "id": "scalezix-p-04",
            "requested_url": "https://scalezix.com/about",
            "final_url": "https://scalezix.com/about-us",
            "canonical_url": "https://scalezix.com/about-us",
            "http_status": 200,
            "title": "About Scalezix - Leadership & Mission",
            "meta_description": "Learn about the mission, engineering leadership, and vision driving Scalezix forward in Ahmedabad and globally.",
            "h1_data": ["Building Software That Scales Without Limits"],
            "language": "en",
            "robots_directives": "index, follow",
            "word_count": 670,
            "internal_link_count": 24,
            "external_link_count": 4,
            "response_time_ms": 290.4,
            "response_size_bytes": 38200,
            "crawl_depth": 1,
            "indexability_status": "indexable",
        },
        {
            "id": "scalezix-p-05",
            "requested_url": "https://scalezix.com/case-studies",
            "final_url": "https://scalezix.com/case-studies",
            "canonical_url": "https://scalezix.com/case-studies",
            "http_status": 200,
            "title": "Client Case Studies & Client Success Stories | Scalezix",
            "meta_description": "Read how Scalezix helped high-growth startups and global enterprises automate processes and scale infrastructure.",
            "h1_data": ["Proven Results for Forward-Thinking Enterprises"],
            "language": "en",
            "robots_directives": "index, follow",
            "word_count": 1420,
            "internal_link_count": 52,
            "external_link_count": 1,
            "response_time_ms": 1380.0,  # Slow response time
            "response_size_bytes": 890000,
            "crawl_depth": 1,
            "indexability_status": "indexable",
        },
        {
            "id": "scalezix-p-06",
            "requested_url": "https://scalezix.com/careers",
            "final_url": "https://scalezix.com/careers",
            "canonical_url": "https://scalezix.com/careers",
            "http_status": 200,
            "title": "Careers at Scalezix - Join Our Engineering Team",
            "meta_description": "Explore engineering and data science career opportunities at Scalezix. Work on transformative projects in Ahmedabad.",
            "h1_data": ["Build the Future of Enterprise AI With Us"],
            "language": "en",
            "robots_directives": "index, follow",
            "word_count": 580,
            "internal_link_count": 19,
            "external_link_count": 2,
            "response_time_ms": 310.0,
            "response_size_bytes": 36400,
            "crawl_depth": 1,
            "indexability_status": "indexable",
        },
        {
            "id": "scalezix-p-07",
            "requested_url": "https://scalezix.com/blog",
            "final_url": "https://scalezix.com/blog",
            "canonical_url": "https://scalezix.com/blog",
            "http_status": 200,
            "title": "Scalezix Tech Blog - Insights on AI, Cloud, and Software Scalability",
            "meta_description": "Read technical deep dives, architectural guides, and AI trends from Scalezix engineers and technology leaders.",
            "h1_data": ["Engineering & Technology Insights"],
            "language": "en",
            "robots_directives": "index, follow",
            "word_count": 720,
            "internal_link_count": 48,
            "external_link_count": 5,
            "response_time_ms": 340.0,
            "response_size_bytes": 48200,
            "crawl_depth": 1,
            "indexability_status": "indexable",
        },
        {
            "id": "scalezix-p-08",
            "requested_url": "https://scalezix.com/blog/scaling-python-backends",
            "final_url": "https://scalezix.com/blog/scaling-python-backends",
            "canonical_url": "https://scalezix.com/blog/scaling-python-backends",
            "http_status": 200,
            "title": "Scaling Python Backends to Millions of Requests",
            "meta_description": "Learn key architectural patterns for scaling FastAPI, asynchronous workers, and SQLAlchemy databases under high traffic loads.",
            "h1_data": ["Scaling Python Backends to Millions of Requests"],
            "language": "en",
            "robots_directives": "index, follow",
            "word_count": 1850,
            "internal_link_count": 16,
            "external_link_count": 8,
            "response_time_ms": 360.0,
            "response_size_bytes": 58900,
            "crawl_depth": 2,
            "indexability_status": "indexable",
        },
        {
            "id": "scalezix-p-09",
            "requested_url": "https://scalezix.com/contact",
            "final_url": "https://scalezix.com/contact",
            "canonical_url": "https://scalezix.com/contact",
            "http_status": 200,
            "title": "Contact Scalezix",
            "meta_description": "Get in touch with our engineering and business team in Ahmedabad to discuss your next project.",
            "h1_data": ["Let's Build Something Exceptional Together"],
            "language": "en",
            "robots_directives": "index, follow",
            "word_count": 210,  # Thin content
            "internal_link_count": 14,
            "external_link_count": 3,
            "response_time_ms": 280.0,
            "response_size_bytes": 24100,
            "crawl_depth": 1,
            "indexability_status": "indexable",
        },
        {
            "id": "scalezix-p-10",
            "requested_url": "https://scalezix.com/legacy-demo",
            "final_url": "https://scalezix.com/legacy-demo",
            "canonical_url": None,
            "http_status": 404,
            "title": "404 Not Found - Scalezix",
            "meta_description": "",
            "h1_data": ["Page Not Found"],
            "language": "en",
            "robots_directives": "noindex",
            "word_count": 80,
            "internal_link_count": 4,
            "external_link_count": 0,
            "response_time_ms": 190.0,
            "response_size_bytes": 12400,
            "crawl_depth": 2,
            "indexability_status": "error",
        },
    ]

    for p in pages_data:
        page_obj = CrawledPage(
            id=p["id"],
            audit_id=sample_audit.id,
            requested_url=p["requested_url"],
            final_url=p["final_url"],
            canonical_url=p["canonical_url"],
            http_status=p["http_status"],
            title=p["title"],
            meta_description=p["meta_description"],
            h1_data=p["h1_data"],
            language=p["language"],
            robots_directives=p["robots_directives"],
            word_count=p["word_count"],
            internal_link_count=p["internal_link_count"],
            external_link_count=p["external_link_count"],
            response_time_ms=p["response_time_ms"],
            response_size_bytes=p["response_size_bytes"],
            crawl_depth=p["crawl_depth"],
            indexability_status=p["indexability_status"],
        )
        db.add(page_obj)

    # 3. SEO Issues & Evidence
    issues_data = [
        {
            "id": "scalezix-iss-01",
            "issue_code": "ERR_HTTP_4XX",
            "title": "Broken Internal Page Returning HTTP 404",
            "category": "crawlability",
            "severity": "critical",
            "priority_score": 88.5,
            "impact": 0.9,
            "confidence": 1.0,
            "estimated_effort": 0.2,
            "description": "A linked internal page returned HTTP 404 Not Found status.",
            "why_it_matters": "Broken links waste crawler budget, prevent indexation, and frustrate users attempting to access company resources.",
            "suggested_fix": "Configure a 301 redirect from /legacy-demo to /services or remove the dead link from the footer.",
            "example_fix": "Redirect 301 /legacy-demo /services",
            "priority_reason": "Urgent priority: High SEO consequence (90% impact) combined with minimal implementation effort makes this an immediate quick-win.",
            "status": "open",
            "affected_page_count": 1,
            "evidences": [
                {
                    "page_url": "https://scalezix.com/legacy-demo",
                    "observed_value": "HTTP Status 404 Not Found",
                    "expected_value": "HTTP Status 200 OK or 301 Permanent Redirect",
                    "evidence_snippet": "Requested URL: https://scalezix.com/legacy-demo -> Status: 404",
                    "evidence_type": "http_status",
                    "explanation": "Page was discovered via internal navigation link but failed to resolve.",
                }
            ],
        },
        {
            "id": "scalezix-iss-02",
            "issue_code": "ERR_IMG_ALT_MISSING",
            "title": "Case Study & Blog Images Missing Alt Attributes",
            "category": "on_page",
            "severity": "medium",
            "priority_score": 74.2,
            "impact": 0.6,
            "confidence": 1.0,
            "estimated_effort": 0.25,
            "description": "Multiple key content images lack descriptive alt text attributes.",
            "why_it_matters": "Alt attributes are necessary for WCAG accessibility compliance and allow Google Image Search to understand image context.",
            "suggested_fix": "Add descriptive alt attributes reflecting the enterprise case study diagrams and team photos.",
            "example_fix": '<img src="/assets/case-study-architecture.png" alt="Cloud Microservices Architecture Diagram for Enterprise Client">',
            "priority_reason": "High priority: Accessible images improve image search discoverability and satisfy WCAG guidelines.",
            "status": "open",
            "affected_page_count": 3,
            "evidences": [
                {
                    "page_url": "https://scalezix.com/case-studies",
                    "observed_value": "3 images missing alt text",
                    "expected_value": "Descriptive alt attribute on all content images",
                    "evidence_snippet": '<img src="/assets/enterprise-dashboard-preview.png">',
                    "evidence_type": "image",
                    "explanation": "Hero case study preview graphic lacks alt attribute.",
                },
                {
                    "page_url": "https://scalezix.com/blog/scaling-python-backends",
                    "observed_value": "2 architecture diagrams missing alt text",
                    "expected_value": "Descriptive alt text for diagrams",
                    "evidence_snippet": '<img src="/blog/diagram-concurrency.svg">',
                    "evidence_type": "image",
                    "explanation": "System architecture diagram lacks alt description.",
                },
            ],
        },
        {
            "id": "scalezix-iss-03",
            "issue_code": "WARN_TITLE_LENGTH",
            "title": "Title Tag Exceeds Recommended 60 Character Limit",
            "category": "on_page",
            "severity": "medium",
            "priority_score": 68.0,
            "impact": 0.5,
            "confidence": 0.9,
            "estimated_effort": 0.15,
            "description": "Page title exceeds 60 characters and will be truncated with an ellipsis in Google SERPs.",
            "why_it_matters": "Truncated titles hide valuable value propositions and reduce organic search click-through rate (CTR).",
            "suggested_fix": "Shorten the title to under 60 characters, keeping primary keywords at the front.",
            "example_fix": "<title>Software Engineering & Cloud Services | Scalezix</title>",
            "priority_reason": "Quick on-page adjustment that immediately improves search snippet appearance.",
            "status": "open",
            "affected_page_count": 2,
            "evidences": [
                {
                    "page_url": "https://scalezix.com/services",
                    "observed_value": "Title length: 82 characters ('Services | Scalezix Software Engineering, AI & Cloud Infrastructure Consulting Services')",
                    "expected_value": "30 to 60 characters",
                    "evidence_snippet": "<title>Services | Scalezix Software Engineering, AI & Cloud Infrastructure Consulting Services</title>",
                    "evidence_type": "title_tag",
                    "explanation": "Title will be cut off after ~60 characters on mobile and desktop Google searches.",
                }
            ],
        },
        {
            "id": "scalezix-iss-04",
            "issue_code": "ERR_META_DESC_MISSING",
            "title": "Missing Meta Description on AI Solutions Page",
            "category": "on_page",
            "severity": "high",
            "priority_score": 79.8,
            "impact": 0.75,
            "confidence": 1.0,
            "estimated_effort": 0.15,
            "description": 'The AI Solutions landing page has no `<meta name="description">` tag.',
            "why_it_matters": "Without an explicit meta description, Google extracts random body text snippets for search snippets, lowering CTR.",
            "suggested_fix": "Add an engaging, keyword-focused meta description between 120 and 155 characters.",
            "example_fix": '<meta name="description" content="Discover Scalezix enterprise AI and machine learning solutions. We build scalable data pipelines, predictive models, and LLM systems.">',
            "priority_reason": "High priority: Significant ranking influence (75% impact) with very low implementation effort.",
            "status": "open",
            "affected_page_count": 1,
            "evidences": [
                {
                    "page_url": "https://scalezix.com/ai-solutions",
                    "observed_value": "Missing meta description",
                    "expected_value": "120-155 characters compelling description",
                    "evidence_snippet": "<head>...meta description missing...</head>",
                    "evidence_type": "meta_description",
                    "explanation": "Critical commercial landing page lacks meta description.",
                }
            ],
        },
        {
            "id": "scalezix-iss-05",
            "issue_code": "WARN_SLOW_RESPONSE_TIME",
            "title": "Slow Response Time on Case Studies Hub (> 1.2s)",
            "category": "performance",
            "severity": "medium",
            "priority_score": 62.4,
            "impact": 0.6,
            "confidence": 0.85,
            "estimated_effort": 0.4,
            "description": "Initial HTML Time-To-First-Byte (TTFB) on the case studies page took 1380ms.",
            "why_it_matters": "High TTFB fails Core Web Vitals thresholds and increases bounce rates on mobile networks.",
            "suggested_fix": "Enable page-level Redis/Varnish caching or optimize un-cached database queries on the case studies endpoint.",
            "example_fix": "Enable Cloudflare HTML edge caching or server-side Redis response caching.",
            "priority_reason": "Core Web Vitals factor with direct impact on user conversion rate.",
            "status": "open",
            "affected_page_count": 1,
            "evidences": [
                {
                    "page_url": "https://scalezix.com/case-studies",
                    "observed_value": "1380.0 ms response time",
                    "expected_value": "Under 600 ms TTFB",
                    "evidence_snippet": "Latency: 1380ms, Size: 890 KB",
                    "evidence_type": "performance_metric",
                    "explanation": "Initial server response latency exceeds recommended threshold.",
                }
            ],
        },
        {
            "id": "scalezix-iss-06",
            "issue_code": "WARN_INTERNAL_LINK_TO_REDIRECT",
            "title": "Internal Link to Redirected URL (/about -> /about-us)",
            "category": "internal_linking",
            "severity": "medium",
            "priority_score": 58.0,
            "impact": 0.5,
            "confidence": 0.95,
            "estimated_effort": 0.15,
            "description": "Site navigation links to /about, which redirects to /about-us.",
            "why_it_matters": "Adds an extra HTTP roundtrip latency for visitors and wastes crawler budget.",
            "suggested_fix": "Update header and footer navigation links to point directly to /about-us.",
            "example_fix": 'Change href="/about" to href="/about-us"',
            "priority_reason": "Trivial link update that eliminates redirect delay.",
            "status": "open",
            "affected_page_count": 1,
            "evidences": [
                {
                    "page_url": "https://scalezix.com/",
                    "observed_value": "Link href='/about' redirects with HTTP 301 to '/about-us'",
                    "expected_value": "Direct link href='/about-us'",
                    "evidence_snippet": '<a href="/about">About Us</a>',
                    "evidence_type": "redirect_link",
                    "explanation": "Primary navigation contains outdated link causing unnecessary redirect.",
                }
            ],
        },
        {
            "id": "scalezix-iss-07",
            "issue_code": "INFO_H1_MULTIPLE",
            "title": "Multiple H1 Headings on Homepage (Review Recommendation)",
            "category": "on_page",
            "severity": "informational",
            "priority_score": 34.5,
            "impact": 0.25,
            "confidence": 0.75,
            "estimated_effort": 0.2,
            "description": "Homepage contains 2 `<h1>` elements.",
            "why_it_matters": "A single primary H1 heading provides clear hierarchy for screen readers and search bots.",
            "suggested_fix": "Keep the main hero heading as H1 and convert 'Our Core Philosophy' to an H2 heading.",
            "example_fix": "Change second <h1> tag to <h2>.",
            "priority_reason": "Semantic hierarchy recommendation for accessibility.",
            "status": "open",
            "affected_page_count": 1,
            "evidences": [
                {
                    "page_url": "https://scalezix.com/",
                    "observed_value": "Found 2 H1 tags",
                    "expected_value": "1 main H1 heading",
                    "evidence_snippet": "<h1>Empowering Enterprises...</h1> and <h1>Our Core Philosophy</h1>",
                    "evidence_type": "heading",
                    "explanation": "Two separate H1 tags detected on the same page.",
                }
            ],
        },
    ]

    for iss in issues_data:
        issue_obj = SEOIssue(
            id=iss["id"],
            audit_id=sample_audit.id,
            issue_code=iss["issue_code"],
            title=iss["title"],
            category=iss["category"],
            severity=iss["severity"],
            priority_score=iss["priority_score"],
            impact=iss["impact"],
            confidence=iss["confidence"],
            estimated_effort=iss["estimated_effort"],
            description=iss["description"],
            why_it_matters=iss["why_it_matters"],
            suggested_fix=iss["suggested_fix"],
            example_fix=iss["example_fix"],
            priority_reason=iss["priority_reason"],
            status=iss["status"],
            affected_page_count=iss["affected_page_count"],
        )
        db.add(issue_obj)
        db.flush()

        for ev in iss["evidences"]:
            ev_obj = IssueEvidence(
                id=str(uuid.uuid4()),
                issue_id=issue_obj.id,
                page_url=ev["page_url"],
                observed_value=ev["observed_value"],
                expected_value=ev["expected_value"],
                evidence_snippet=ev["evidence_snippet"],
                evidence_type=ev["evidence_type"],
                explanation=ev["explanation"],
            )
            db.add(ev_obj)

    # 4. Crawl Events
    events_data = [
        ("info", "Audit initiated for target https://scalezix.com"),
        ("robots", "robots.txt verified: Allowed crawling with standard bot policy"),
        ("crawl_page", "Crawled root landing page: https://scalezix.com/ (Status 200)"),
        ("crawl_page", "Discovered & crawled 18 internal routes"),
        (
            "complete",
            "Crawl completed successfully. 18 pages indexed, 7 SEO issue types detected.",
        ),
    ]
    for ev_type, msg in events_data:
        db.add(
            CrawlEvent(
                id=str(uuid.uuid4()),
                audit_id=sample_audit.id,
                event_type=ev_type,
                message=msg,
            )
        )

    db.commit()
    return sample_audit
