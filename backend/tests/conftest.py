"""Shared pytest fixtures for the backend test suite."""

import pytest


@pytest.fixture
def client():
    """Return a TestClient wrapping a freshly constructed application.

    Imports are performed lazily so test modules that do not need the full web
    stack (e.g. the YouCam integration unit tests) can run without it installed.
    """

    from fastapi.testclient import TestClient

    from app.main import create_app

    return TestClient(create_app())
