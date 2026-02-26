"""Database session and engine."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from models import Base

url = settings.database_url_normalized
connect_args = {} if url.startswith("postgresql") else {"check_same_thread": False}
engine = create_engine(
    url,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency that yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
