"""Application configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings loaded from environment."""

    # JWT-like static API key (header: X-API-Key)
    api_key: str = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "dXNlcjpkaXJlY3RvcnktYXBp."
        "L1kW3o0Uu9iJt0Kr8o8w0g"
    )
    database_url: str = "sqlite:///./test.db"
    # For PostgreSQL: postgresql://user:password@host:5432/dbname

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def database_url_normalized(self) -> str:
        """SQLAlchemy expects postgresql:// not postgres://."""
        u = self.database_url
        if u.startswith("postgres://"):
            return u.replace("postgres://", "postgresql://", 1)
        return u


settings = Settings()
