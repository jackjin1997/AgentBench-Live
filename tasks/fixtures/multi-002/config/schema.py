from pydantic import BaseModel


class AppConfig(BaseModel):
    """Application configuration schema."""

    app_name: str
    debug: bool = False
    log_level: str = "INFO"
    max_connections: int = 100
    api_key: str = ""
