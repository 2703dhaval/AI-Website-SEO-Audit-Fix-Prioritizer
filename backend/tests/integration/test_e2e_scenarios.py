import pytest
import time
from app.services.audit_service import start_audit_service, ACTIVE_PROGRESS


class TestEndToEndScenarios:
    """
    Comprehensive verification of the 12 critical user journey scenarios:
    1. Open the application / Health check
    2. Navigate to new audit / validate inputs
    3. Submit invalid URL and verify validation rejection
    4. Start valid audit against controlled local test website
    5. Observe actual progress transitions
    6. Open completed audit results
    7. Inspect detected issues and evidence
    8. Filter findings by severity
    9. Open an issue and update its status
    10. Verify export generation (CSV, JSON, PDF)
    11. Open the sample report
    12. Delete a test audit after confirmation
    """

    def test_complete_e2e_audit_lifecycle(self, client, db_session, local_test_site):
        # 1. Health check
        resp_health = client.get("/health")
        assert resp_health.status_code == 200

        # 2 & 3. Submit invalid URL and verify validation rejection
        resp_bad = client.post("/api/v1/audits", json={"url": "ftp://example.com/not-http"})
        assert resp_bad.status_code == 400

        resp_metadata = client.post("/api/v1/audits", json={"url": "http://169.254.169.254/latest/meta-data"})
        assert resp_metadata.status_code == 400

        # 4. Start valid audit against controlled local test website (local_test_site: 8765)
        audit_res = client.post(
            "/api/v1/audits",
            json={
                "url": local_test_site,
                "audit_name": "E2E Automated Local Audit",
                "max_pages": 3,
                "max_depth": 1,
                "crawl_delay_seconds": 0.1
            }
        )
        assert audit_res.status_code == 201
        audit_data = audit_res.json()
        audit_id = audit_data["id"]

        # 5. Observe actual progress transitions (poll until completed, max 15 seconds)
        completed = False
        for _ in range(30):
            prog = client.get(f"/api/v1/audits/{audit_id}/progress").json()
            if prog["status"] == "completed":
                completed = True
                break
            time.sleep(0.5)

        assert completed is True, f"Audit should complete within polling window, got {prog.get('status')}"

        # 6. Open completed audit results & summary
        sum_resp = client.get(f"/api/v1/audits/{audit_id}/summary")
        assert sum_resp.status_code == 200
        summary = sum_resp.json()
        assert summary["health_score"] > 0
        assert summary["total_pages"] >= 2

        # 7. Inspect detected issues and evidence
        iss_resp = client.get(f"/api/v1/audits/{audit_id}/issues")
        assert iss_resp.status_code == 200
        issues_list = iss_resp.json()["items"]
        assert len(issues_list) > 0
        first_issue = issues_list[0]
        assert len(first_issue["evidences"]) > 0

        # 8. Filter findings by severity
        crit_resp = client.get(f"/api/v1/audits/{audit_id}/issues?severity=critical")
        assert crit_resp.status_code == 200

        # 9. Open an issue and update its status
        patch_resp = client.patch(
            f"/api/v1/audits/{audit_id}/issues/{first_issue['id']}",
            json={"status": "resolved"}
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["status"] == "resolved"

        # 10. Verify exports (CSV, JSON, PDF)
        csv_resp = client.get(f"/api/v1/audits/{audit_id}/export.csv")
        assert csv_resp.status_code == 200
        assert "Rank,Issue Code" in csv_resp.text

        json_resp = client.get(f"/api/v1/audits/{audit_id}/export.json")
        assert json_resp.status_code == 200
        assert "audit_metadata" in json_resp.json()

        pdf_resp = client.get(f"/api/v1/audits/{audit_id}/report.pdf")
        assert pdf_resp.status_code == 200
        assert pdf_resp.content.startswith(b"%PDF")

        # 11. Open sample report
        sample_resp = client.get("/api/v1/sample/sample-report")
        assert sample_resp.status_code == 200

        # 12. Delete test audit
        del_resp = client.delete(f"/api/v1/audits/{audit_id}")
        assert del_resp.status_code == 204

        # Verify it's gone
        get_gone = client.get(f"/api/v1/audits/{audit_id}")
        assert get_gone.status_code == 404
