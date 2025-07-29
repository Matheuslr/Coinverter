import pytest

from tests.conftest import TestClient


def test_should_get_docs(client: TestClient):
    response = client.get("/docs")

    assert response.status_code == 200


def test_should_get_swagger_redirect(client: TestClient):
    response = client.get("/swagger-redirect")

    assert response.status_code == 200


def test_should_get_redoc(client: TestClient):
    response = client.get("/redoc")

    assert response.status_code == 200
