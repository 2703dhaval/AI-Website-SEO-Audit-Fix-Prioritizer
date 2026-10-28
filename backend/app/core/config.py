from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SEO Audit Pro"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./seo_audit.db"

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # Crawler Defaults & Limits
    CRAWLER_USER_AGENT: str = (
        "SEOAuditProBot/1.0 (+https://scalezix.com/bot; technical-audit)"
    )
    MAX_CRAWL_PAGES: int = 50
    DEFAULT_CRAWL_PAGES: int = 25
    MAX_CRAWL_DEPTH: int = 5
    DEFAULT_CRAWL_DEPTH: int = 3
    REQUEST_TIMEOUT_SECONDS: float = 10.0
    REQUEST_DELAY_SECONDS: float = 0.5
    MAX_RESPONSE_BYTES: int = 5 * 1024 * 1024  # 5 MB max per page
    MAX_REDIRECTS: int = 5

    # SSRF Protection
    ALLOW_LOCAL_TEST_DOMAINS: bool = True  # Allows local test-site like test.local / 127.0.0.1 when explicitly flagged for automated tests

    # Optional LLM integration
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()
