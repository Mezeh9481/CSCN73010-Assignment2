"""Shared Flask test client."""

import pytest

from app import app


@pytest.fixture
def client():
    """Return a Flask client with exceptions visible to pytest."""
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client
