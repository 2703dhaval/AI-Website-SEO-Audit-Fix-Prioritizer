import pytest
from app.services.sample_report_data import SAMPLE_AUDIT_ID


class TestAPIEndpoints:
    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("healthy", "degraded")
        assert "database" in data
        assert "version" in data

    def test_sample_report_endpoint(self, client):
        resp = client.get("/api/v1/sample/sample-report")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == SAMPLE_AUDIT_ID
        assert data["normalized_domain"] == "scalezix.com"
        assert data["seo_health_score"] > 0

    def test_dashboard_stats(self, client):
        resp = client.get("/api/v1/dashboard/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_audits" in data
        assert "websites_audited" in data
        assert "total_issues" in data
        assert "avg_health_score" in data
        assert "severity_distribution" in data

    def test_list_audits(self, client):
        resp = client.get("/api/v1/audits")
        assert resp.status_code == 200
        items = resp.json()
        assert isinstance(items, list)
        assert len(items) >= 1  # Sample audit exists

    def test_get_audit_by_id(self, client):
        resp = client.get(f"/api/v1/audits/{SAMPLE_AUDIT_ID}")
        assert resp.status_code == 200
        assert resp.json()["id"] == SAMPLE_AUDIT_ID

        # Nonexistent audit
        resp_404 = client.get("/api/v1/audits/nonexistent-uuid")
        assert resp_404.status_code == 404

    def test_get_audit_pages(self, client):
        resp = client.get(f"/api/v1/audits/{SAMPLE_AUDIT_ID}/pages?page=1&limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) > 0

    def test_get_audit_issues_and_patch_status(self, client):
        # List issues
        resp = client.get(f"/api/v1/audits/{SAMPLE_AUDIT_ID}/issues")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) > 0
        first_issue = data["items"][0]
        issue_id = first_issue["id"]

        # Detail
        resp_det = client.get(f"/api/v1/audits/{SAMPLE_AUDIT_ID}/issues/{issue_id}")
        assert resp_det.status_code == 200
        assert resp_det.json()["id"] == issue_id

        # Update status to in_progress
        resp_patch = client.patch(
            f"/api/v1/audits/{SAMPLE_AUDIT_ID}/issues/{issue_id}",
            json={"status": "in_progress"}
        )
        assert resp_patch.status_code == 200
        assert resp_patch.json()["status"] == "in_progress"

        # Invalid status
        resp_bad = client.patch(
            f"/api/v1/audits/{SAMPLE_AUDIT_ID}/issues/{issue_id}",
            json={"status": "invalid_status_xyz"}
        )
        assert resp_bad.status_code == 400

    def test_audit_summary(self, client):
        resp = client.get(f"/api/v1/audits/{SAMPLE_AUDIT_ID}/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "health_score" in data
        assert "severity_breakdown" in data
        assert "category_breakdown" in data
        assert "top_priority_fixes" in data

    def test_audit_exports(self, client):
        # CSV
        resp_csv = client.get(f"/api/v1/audits/{SAMPLE_AUDIT_ID}/export.csv")
        assert resp_csv.status_code == 200
        assert "text/csv" in resp_csv.headers["content-type"]
        assert "attachment" in resp_csv.headers["content-disposition"]

        # JSON
        resp_json = client.get(f"/api/v1/audits/{SAMPLE_AUDIT_ID}/export.json")
        assert resp_json.status_code == 200
        assert "audit_metadata" in resp_json.json()

        # PDF
        resp_pdf = client.get(f"/api/v1/audits/{SAMPLE_AUDIT_ID}/report.pdf")
        assert resp_pdf.status_code == 200
        assert resp_pdf.headers["content-type"] == "application/pdf"
        assert resp_pdf.content.startswith(b"%PDF")

    def test_create_audit_validation_failures(self, client):
        # Invalid URL scheme
        resp_scheme = client.post("/api/v1/audits", json={"url": "ftp://example.com"})
        assert resp_scheme.status_code == 400

        # Disallowed SSRF target
        resp_ssrf = client.post("/api/v1/audits", json={"url": "http://169.254.169.254/latest/meta-data"})
        assert resp_ssrf.status_code == 400
