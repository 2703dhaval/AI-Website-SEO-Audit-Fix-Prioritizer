import pytest
from app.reports.csv_export import sanitize_csv_cell, generate_issues_csv
from app.reports.json_export import generate_audit_json
from app.reports.pdf_generator import generate_audit_pdf
from datetime import datetime, timezone


class MockAudit:
    id = "audit-12345"
    audit_name = "Test Audit"
    submitted_url = "https://example.com"
    normalized_domain = "example.com"
    status = "completed"
    seo_health_score = 85.0
    scoring_version = "v1.0"
    total_discovered_pages = 5
    total_crawled_pages = 5
    started_at = datetime.now(timezone.utc)
    completed_at = datetime.now(timezone.utc)
    created_at = datetime.now(timezone.utc)
    crawl_policy_summary = "Crawl permitted"


class MockIssue:
    id = "issue-01"
    issue_code = "ERR_TITLE_MISSING"
    title = "Missing Title"
    category = "on_page"
    severity = "critical"
    priority_score = 92.0
    impact = 0.95
    confidence = 1.0
    estimated_effort = 0.1
    status = "open"
    affected_page_count = 1
    description = "No title"
    why_it_matters = "High importance"
    suggested_fix = "Add title"
    example_fix = "<title>Hello</title>"
    priority_reason = "Quick win"
    evidences = []


class MockPage:
    id = "page-01"
    requested_url = "https://example.com"
    final_url = "https://example.com"
    http_status = 200
    title = "Home"
    meta_description = "Desc"
    word_count = 350
    internal_link_count = 10
    external_link_count = 2
    response_time_ms = 220.0
    response_size_bytes = 15000
    crawl_depth = 0
    indexability_status = "indexable"


class TestExports:
    def test_csv_formula_injection_sanitization(self):
        # Formula characters: =, +, -, @
        assert sanitize_csv_cell("=1+1") == "'=1+1"
        assert sanitize_csv_cell("+cmd|' /C calc'!A0") == "'+cmd|' /C calc'!A0"
        assert sanitize_csv_cell("-5+2") == "'-5+2"
        assert sanitize_csv_cell("@SUM(A1:A5)") == "'@SUM(A1:A5)"
        assert sanitize_csv_cell("Normal Text Title") == "Normal Text Title"

    def test_generate_csv(self):
        csv_str = generate_issues_csv(MockAudit(), [MockIssue()])
        assert "Rank,Issue Code,Title,Category,Severity" in csv_str
        assert "ERR_TITLE_MISSING" in csv_str
        assert "Missing Title" in csv_str

    def test_generate_json(self):
        json_obj = generate_audit_json(MockAudit(), [MockPage()], [MockIssue()])
        assert "audit_metadata" in json_obj
        assert json_obj["audit_metadata"]["id"] == "audit-12345"
        assert len(json_obj["pages"]) == 1
        assert len(json_obj["issues"]) == 1

    def test_generate_pdf(self):
        pdf_bytes = generate_audit_pdf(MockAudit(), [MockPage()], [MockIssue()])
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 500
        assert pdf_bytes.startswith(b"%PDF")  # Valid PDF header
