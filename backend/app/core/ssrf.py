import ipaddress
import socket
from urllib.parse import urlparse


class SSRFValidationError(ValueError):
    """Raised when a URL violates SSRF safety constraints."""


# Disallowed IPv4 networks
DISALLOWED_IPV4_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),  # Current network (only valid as source address)
    ipaddress.ip_network("10.0.0.0/8"),  # RFC 1918 Private
    ipaddress.ip_network("127.0.0.0/8"),  # Loopback
    ipaddress.ip_network(
        "169.254.0.0/16"
    ),  # Link-local / Cloud metadata (AWS, GCP, Azure)
    ipaddress.ip_network("172.16.0.0/12"),  # RFC 1918 Private
    ipaddress.ip_network("192.0.0.0/24"),  # IETF Protocol Assignments
    ipaddress.ip_network("192.0.2.0/24"),  # TEST-NET-1
    ipaddress.ip_network("192.168.0.0/16"),  # RFC 1918 Private
    ipaddress.ip_network("198.18.0.0/15"),  # Network benchmark tests
    ipaddress.ip_network("198.51.100.0/24"),  # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),  # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),  # Multicast
    ipaddress.ip_network("240.0.0.0/4"),  # Reserved / Future use
    ipaddress.ip_network("255.255.255.255/32"),  # Broadcast
]

# Disallowed IPv6 networks
DISALLOWED_IPV6_NETWORKS = [
    ipaddress.ip_network("::1/128"),  # Loopback
    ipaddress.ip_network("::/128"),  # Unspecified
    ipaddress.ip_network("::ffff:0:0/96"),  # IPv4-mapped IPv6
    ipaddress.ip_network("64:ff9b::/96"),  # IPv4/IPv6 translation
    ipaddress.ip_network("100::/64"),  # Discard-only prefix
    ipaddress.ip_network("2001:db8::/32"),  # Documentation
    ipaddress.ip_network("fc00::/7"),  # Unique local address (ULA)
    ipaddress.ip_network("fe80::/10"),  # Link-local unicast
    ipaddress.ip_network("ff00::/8"),  # Multicast
]

# Known cloud metadata hostnames
DISALLOWED_HOSTNAMES = {
    "instance-data",
    "metadata.google.internal",
    "metadata.goog",
    "169.254.169.254",
}


def is_ip_disallowed(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Checks whether an IP address belongs to any private, loopback, or reserved network."""
    if isinstance(ip, ipaddress.IPv4Address):
        for net in DISALLOWED_IPV4_NETWORKS:
            if ip in net:
                return True
    elif isinstance(ip, ipaddress.IPv6Address):
        for net in DISALLOWED_IPV6_NETWORKS:
            if ip in net:
                return True
        # Also check for IPv4-mapped addresses
        if ip.ipv4_mapped:
            return is_ip_disallowed(ip.ipv4_mapped)
    return False


def validate_url_ssrf(
    url: str, allow_test_mode: bool = False
) -> tuple[bool, str | None, str | None]:
    """
    Validates a URL against SSRF attacks.
    Returns (is_valid, resolved_ip, error_message).
    """
    if not url or not isinstance(url, str):
        return False, None, "URL must be a non-empty string"

    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, None, f"Malformed URL: {e}"

    # 1. Scheme check: only http and https are permitted
    if parsed.scheme.lower() not in ("http", "https"):
        return (
            False,
            None,
            f"Scheme '{parsed.scheme}' is not permitted. Only HTTP and HTTPS are allowed.",
        )

    # 2. Reject credentials in URL (e.g., http://user:pass@domain.com)
    if parsed.username or parsed.password:
        return False, None, "URLs containing embedded credentials are not allowed."

    # 3. Hostname check
    hostname = parsed.hostname
    if not hostname:
        return False, None, "URL is missing a valid hostname."

    hostname_lower = hostname.lower()

    # Check disallowed hostnames
    if hostname_lower in DISALLOWED_HOSTNAMES:
        return False, None, f"Access to restricted host '{hostname}' is blocked."

    # Test mode exception for explicitly permitted local test suites
    if allow_test_mode and (
        hostname_lower in ("localhost", "127.0.0.1", "testserver", "local-test.seo")
        or hostname_lower.endswith(".local")
    ):
        return True, "127.0.0.1", None

    # Check localhost explicitly
    if hostname_lower in (
        "localhost",
        "localhost.localdomain",
    ) or hostname_lower.endswith(".localhost"):
        return False, None, "Access to localhost domains is prohibited."

    # 4. Port check (standard web ports or safe range)
    port = parsed.port
    if port is not None and port not in (80, 443, 8080, 8443):
        if not allow_test_mode:
            return (
                False,
                None,
                f"Port {port} is not allowed. Only ports 80, 443, 8080, and 8443 are supported.",
            )

    # 5. Resolve DNS and check all resulting IPs
    try:
        # Check if the hostname itself is already an IP address
        try:
            ip_obj = ipaddress.ip_address(hostname)
            if is_ip_disallowed(ip_obj):
                return (
                    False,
                    str(ip_obj),
                    f"Direct IP address {ip_obj} is in a private, loopback, or reserved range.",
                )
            return True, str(ip_obj), None
        except ValueError:
            pass  # Not an IP string, continue to DNS resolution

        addr_info = socket.getaddrinfo(
            hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM
        )
        if not addr_info:
            return False, None, f"Unable to resolve hostname '{hostname}'"

        first_ip = None
        for family, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)
            if not first_ip:
                first_ip = ip_str

            if is_ip_disallowed(ip_obj):
                return (
                    False,
                    ip_str,
                    f"Hostname '{hostname}' resolves to restricted IP address {ip_str}.",
                )

        return True, first_ip, None

    except socket.gaierror as e:
        return False, None, f"DNS resolution failed for hostname '{hostname}': {e}"
    except Exception as e:
        return False, None, f"Validation error during SSRF check: {e}"
