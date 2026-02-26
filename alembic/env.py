import os
from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config
url = os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url") or "sqlite:///./test.db"
# PostgreSQL URL may use postgres://; SQLAlchemy expects postgresql://
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)
config.set_main_option("sqlalchemy.url", url)

from models import Base
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        {"sqlalchemy.url": url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()