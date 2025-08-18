from logging.config import fileConfig

from model.user_tokens import UserTokens
from model.users import User
from model.one_time_password import OneTimePassword
from model.email import Email
from model.question import Question
from model.test_case import TestCase
from model.submit import Submit
from model.base import Base
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from util.config import get_config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_database_config():
    ssl_ca_path = get_config("DATABASE_SSL_CA", "")
    if ssl_ca_path:
        connect_args = {"ssl_ca": ssl_ca_path}
    else:
        connect_args = {"ssl": {}}

    host = get_config("DATABASE_HOST", "localhost")
    port = get_config("DATABASE_PORT", "3306")
    user = get_config("DATABASE_USERNAME", "root")
    password = get_config("DATABASE_PASSWORD", "root")
    database = get_config("DATABASE_NAME", "tongla-hub")

    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?ssl=VERIFY_IDENTITY&ssl_ca={ssl_ca_path}"

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_config()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

config.set_main_option("sqlalchemy.url", get_database_config())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
