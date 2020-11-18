"""
TODO
"""
import os

import pytest

from app import application, _init_flask_app, db_session


@pytest.fixture(autouse=True)
def client():
    _init_flask_app(application, "config.TestConfiguration")
    ctx = application.app_context()
    ctx.push()

    with application.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def db():
    yield db_session
    db_session.remove()
