# pylint: disable=redefined-outer-name
import pytest
from firefly import create_app


@pytest.fixture
def app():
    app = create_app()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
