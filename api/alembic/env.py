from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# App imports work because alembic.ini sets `prepend_sys_path = .` and alembic
# is run from api/, so `app` is the top-level package.
from app.config import get_settings
from app.database import Base

# Import every module that defines tables so they register on Base.metadata.
from app.auth import model as _auth_model  # noqa: F401
from app.blog import model as _blog_model  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The .env file is the single source of truth for the database URL.
config.set_main_option("sqlalchemy.url", get_settings().database_url)

target_metadata = Base.metadata

# SQLite cannot ALTER most things in place; render_as_batch lets Alembic
# rebuild-and-copy tables. Harmless on other backends.
_is_sqlite = get_settings().database_url.startswith("sqlite")


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=_is_sqlite,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=_is_sqlite,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
