"""
S0 Smoke Test — verify that the FastAPI app can be imported.

This test does NOT start the ASGI server, does NOT trigger lifespan
(no Redis/DB connections), and does NOT import models directly.
Environment variables are set by conftest.py before this runs.
"""
from fastapi import FastAPI


def test_app_is_fastapi_instance():
    """Importing app.main should produce a valid FastAPI instance."""
    from app.main import app

    assert isinstance(app, FastAPI)
