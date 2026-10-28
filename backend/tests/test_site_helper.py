import sys
import os

# Add test-site directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "test-site")))
from server import run_test_server


def start_mock_test_site(port: int = 8765):
    return run_test_server(port)
