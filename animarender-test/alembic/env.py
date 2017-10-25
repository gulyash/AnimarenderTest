import logging.config
import os
import sys

import alembic
from sqlalchemy import engine_from_config
from sqlalchemy import pool


def _join_path_absolute(path, *paths):
    """
    Works like ``os.path.join`` but also expands any wildcards and placeholders
    like ``.``, ``..``, ``~`` or duplicated separators and normalizes the path
    according to current OS rules.

    :param str path: The initial path.
    :param str paths: Path components to join.
    :return str: Normalized absolute joined path.
    """
    path = os.path.join(path, *paths)
    path = os.path.expanduser(path)
    path = os.path.abspath(path)
    path = os.path.normpath(path)
    return path


# Add 'src' directory to sys.path in order to access our modules.
sys.path.insert(
    0, _join_path_absolute(os.path.dirname(__file__), '../src'))

import config
import database.meta
import database.client

# This is the Alembic Config object, which provides access to the values within
# the .ini file in use.
configuration = alembic.context.config
configuration.set_main_option(
    'sqlalchemy.url',
    'mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}'
    .format(**config.DATABASE_CONFIG))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
logging.config.fileConfig(configuration.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support.
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = database.meta.DeclarativeBase.metadata

# Other values from the config, defined by the needs of env.py, can be acquired:
# my_important_option = config.get_main_option('my_important_option')
# ... etc.


def run_migrations_offline():
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine, though
    an Engine is acceptable here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the script output.
    """
    url = configuration.get_main_option("sqlalchemy.url")
    alembic.context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )

    with alembic.context.begin_transaction():
        alembic.context.run_migrations()


def run_migrations_online():
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection
    with the context.
    """
    database.client.DatabaseClient.load_models()
    connectable = engine_from_config(
        configuration.get_section(configuration.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        alembic.context.configure(
            connection=connection,
            target_metadata=target_metadata,
            sqlalchemy_module_prefix='sqlalchemy.',
        )

        with alembic.context.begin_transaction():
            alembic.context.run_migrations()


if alembic.context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
