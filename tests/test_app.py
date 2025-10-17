import os
import sys
import pytest

from app import app 

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json["message"] == "Welcome to the Flask CI/CD Demo!"

def test_health_route(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"