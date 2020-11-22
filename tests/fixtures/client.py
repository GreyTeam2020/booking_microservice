import os

import pytest

from app import application, _init_flask_app


@pytest.fixture(autouse=True)
def client():
    _init_flask_app(application, "config.TestConfiguration")
    ctx = application.app_context()
    ctx.push()

    with application.test_client() as client:
        yield client