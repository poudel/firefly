# pylint: disable=redefined-outer-name
import pytest
from firefly import create_app


@pytest.fixture
def app():
    app = create_app({"TESTING": True})

    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()


@pytest.fixture
def client(app):
    return app.test_client()
