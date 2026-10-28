import pytest
from app.core.ssrf import validate_url_ssrf, is_ip_disallowed
import ipaddress


class TestSSRFProtection:
    @pytest.mark.parametrize("disallowed_url", [
        "http://localhost",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.1:8000",
        "http://127.0.1.1",
        "http://0.0.0.0",
        "http://10.0.0.1",
        "http://10.254.12.3",
        "http://172.16.0.1",
        "http://172.31.255.255",
        "http://192.168.1.1",
        "http://192.168.100.50",
        "http://169.254.169.254",  # AWS/GCP/Azure instance metadata
        "http://169.254.1.1",      # Link local
        "http://instance-data",
        "http://metadata.google.internal",
        "http://metadata.goog",
        "http://[::1]",            # IPv6 loopback
        "http://[fc00::1]",        # IPv6 unique local
        "http://[fe80::1]",        # IPv6 link-local
    ])
    def test_ssrf_blocks_private_and_loopback_addresses(self, disallowed_url):
        is_safe, ip, err = validate_url_ssrf(disallowed_url, allow_test_mode=False)
        assert not is_safe, f"Expected {disallowed_url} to be blocked by SSRF firewall, but passed!"
        assert err is not None

    @pytest.mark.parametrize("invalid_scheme_url", [
        "file:///etc/passwd",
        "file://c:/windows/win.ini",
        "ftp://example.com/file.txt",
        "gopher://example.com",
        "dict://example.com",
        "data:text/html,<h1>Hello</h1>",
        "javascript:alert(1)",
    ])
    def test_ssrf_rejects_non_http_schemes(self, invalid_scheme_url):
        is_safe, _, err = validate_url_ssrf(invalid_scheme_url)
        assert not is_safe
        assert "Only HTTP and HTTPS are allowed" in err or "Scheme" in err

    def test_ssrf_rejects_credentials_in_url(self):
        url = "http://admin:secretPassword123@example.com/page"
        is_safe, _, err = validate_url_ssrf(url)
        assert not is_safe
        assert "embedded credentials" in err.lower()

    @pytest.mark.parametrize("unsupported_port_url", [
        "http://example.com:22",    # SSH
        "http://example.com:25",    # SMTP
        "http://example.com:3306",  # MySQL
        "http://example.com:5432",  # PostgreSQL
        "http://example.com:6379",  # Redis
        "http://example.com:27017", # MongoDB
    ])
    def test_ssrf_rejects_restricted_ports(self, unsupported_port_url):
        is_safe, _, err = validate_url_ssrf(unsupported_port_url, allow_test_mode=False)
        assert not is_safe
        assert "Port" in err and "not allowed" in err

    def test_ssrf_permits_public_fqdn(self):
        # Scalezix public domain
        is_safe, ip, err = validate_url_ssrf("https://scalezix.com", allow_test_mode=False)
        # Note: If running offline with mock DNS or gaierror, check behavior
        # In standard network environment it resolves to a valid public IP
        assert err is None or "DNS resolution failed" in err or is_safe

    def test_test_mode_permits_local_test_site(self):
        is_safe, ip, err = validate_url_ssrf("http://127.0.0.1:8765", allow_test_mode=True)
        assert is_safe
        assert ip == "127.0.0.1"
        assert err is None
