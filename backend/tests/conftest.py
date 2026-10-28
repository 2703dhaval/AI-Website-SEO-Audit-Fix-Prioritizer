import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services.sample_report_data import seed_sample_company_audit
from test_site_helper import start_mock_test_site

# Use dedicated test sqlite database
TEST_DATABASE_URL = "sqlite:///./test_seo_audit.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Ensure background workers in audit_service use the test engine and session
from app.db import session as db_session_module
db_session_module.SessionLocal = TestingSessionLocal
db_session_module.engine = test_engine


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    # Seed sample audit in test database
    db = TestingSessionLocal()
    seed_sample_company_audit(db)
    db.close()
    
    yield
    
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_seo_audit.db"):
        try:
            os.remove("./test_seo_audit.db")
        except Exception:
            pass


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def local_test_site():
    """Starts the local test HTTP server on port 8765 for automated testing."""
    server = start_mock_test_site(port=8765)
    yield "http://127.0.0.1:8765"
    server.shutdown()
