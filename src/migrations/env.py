from logging.config import fileConfig
from typing import List

from sqlalchemy import pool, engine_from_config

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

import re

rec = {}

# db_names = config.get_main_option('databases')
# print(db_names)
# for name in re.split(r',\s*', db_names):
#     # engines[name] = {}
#     rec['engine'] = engine_from_config(
#         config.get_section(name),
#         prefix='sqlalchemy.',
#         poolclass=pool.NullPool
#     )

# config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.core.config import DB_DSN
from app.db.database import db #, load_modules
from app import server

db.init_app(server.app)

# load_modules()
config.set_main_option("sqlalchemy.url", str(DB_DSN))
target_metadata = db

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


# def _include_object(target_schema):
#     def include_object(obj, name, object_type, reflected, compare_to):
#         if object_type == "table":
#             return obj.schema in target_schema
#         else:
#             return True
#
#     return include_object
#
#
# def _run_migrations_offline(target_metadata, schema):
#     """Run migrations in 'offline' mode.
#
#     This configures the context with just a URL
#     and not an Engine, though an Engine is acceptable
#     here as well.  By skipping the Engine creation
#     we don't even need a DBAPI to be available.
#
#     Calls to context.execute() here emit the given string to the
#     script output.
#
#     """
#     url = config.get_main_option("sqlalchemy.url")
#     context.configure(
#         url=url,
#         target_metadata=target_metadata,
#         literal_binds=True,
#         dialect_opts={"paramstyle": "named"},
#         include_schemas=True,  #1
#         include_object=_include_object(schema),  #1
#         compare_type=True,
#     )
#
#     with context.begin_transaction():
#         context.run_migrations()
#
#
# def _run_migrations_online(target_metadata, schema):
#     """Run migrations in 'online' mode.
#
#     In this scenario we need to create an Engine
#     and associate a connection with the context.
#
#     """
#     connectable = engine_from_config(
#         config.get_section(config.config_ini_section),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#         url = config.get_main_option("sqlalchemy.url"),
#     )
#
#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection,
#             target_metadata=target_metadata,
#             include_schemas=True,  #2
#             include_object=_include_object(schema),  #2
#             compare_type=True,
#         )
#
#         with context.begin_transaction():
#             context.run_migrations()
#
#
# def run_migrations(metadata: db, schema: List[str]):
#     if context.is_offline_mode():
#         _run_migrations_offline(metadata, schema)
#     else:
#         _run_migrations_online(metadata, schema)




def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    # connectable = create_engine(DATABASE_URL)

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
