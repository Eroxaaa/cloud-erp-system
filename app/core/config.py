from functools import lru_cache
import os


class Settings:
    """Application settings loaded from environment variables."""

    project_name: str
    api_version: str
    database_url: str

    admin_username: str
    admin_password: str
    auth_token: str

    cors_origins: list[str]

    def __init__(self) -> None:
        self.project_name = os.getenv("PROJECT_NAME", "Wholesale Clothing ERP API")
        self.api_version = os.getenv("API_VERSION", "1.0.0")
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./erp_crm_wms.db")

        self.admin_username = os.getenv("ERP_ADMIN_USERNAME", "admin")
        self.admin_password = os.getenv("ERP_ADMIN_PASSWORD", "admin123")
        self.auth_token = os.getenv("ERP_AUTH_TOKEN", "wholesale-erp-demo-token")

        self.cors_origins = [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "*").split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
