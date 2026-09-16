import pytest
from app.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    """Test that the home page loads successfully and returns HTTP 200."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"AWS Highly Available Web App" in response.data
    assert b"Application Status: Online" in response.data


def test_health_check(client):
    """Test that the /health endpoint returns HTTP 200 and 'healthy'."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.data.decode("utf-8") == "healthy"
