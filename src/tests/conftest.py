import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import create_engine

from app.core import config as app_config
from app.db.database import db
from app.server import app


# def status(self):
#     return "Pool size: %d  Connections in pool: %d " \
#            "Current Overflow: %d Current Checked out " \
#            "connections: %d" % (self.size(),
#                                 self.checkedin(),
#                                 self.overflow(),
#                                 self.checkedout())


@pytest.fixture
def client():
    return AsyncClient(app=app, base_url="http://127.0.0.1:8000")


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    # create test db
    sqlalchemy_engine = create_engine(app_config.DB_DSN)

    with sqlalchemy_engine.connect() as conn:
        conn.execute("commit")
        conn.execute(f"CREATE DATABASE {app_config.TEST_DB_NAME};")
        conn.close()
    sqlalchemy_engine.dispose()

    test_sqlalchemy_engine = create_engine(app_config.TEST_DB_DSN)
    db.create_all(bind=test_sqlalchemy_engine)
    test_sqlalchemy_engine.dispose()
    # from app.db.models import Base
    # Base = declarative_base()
    # Base.metadata.create_all(bind=test_sqlalchemy_engine)


def pytest_sessionfinish(session, exitstatus):
    """
    Cal led after whole test run finished, right before
    returning the exit status to the system.
    """
    # drop test db
    sqlalchemy_engine = create_engine(app_config.DB_DSN)
    with sqlalchemy_engine.connect() as conn:
        conn.execute("commit")
        conn.execute(f"DROP DATABASE {app_config.TEST_DB_NAME}")  # WITH (FORCE);
        conn.close()
    sqlalchemy_engine.dispose()


def pytest_unconfigure(config):
    """
    called before test process is exited.
    """
