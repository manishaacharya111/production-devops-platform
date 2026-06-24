import pytest
from app import app

#A fixture is a reusable setup function. Every test that needs to make HTTP requests to your 
# Flask app needs a test client. Instead of setting this up in every single test function, 
# you define it once as a fixture and pytest automatically passes it to any test that asks for 
# it by name.
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client: # It simulates making real HTTP requests to your app without actually starting a server or opening a network port. Everything happens in memory.
        yield client           #  the fixture gives the test client to the test, the test runs, then cleanup happens after yield. It's like a try/finally pattern

def test_home_returns_200(client):  # does / respond at all?
    response = client.get('/')
    assert response.status_code == 200

def test_home_returns_json(client): # does / return the right data?
    response = client.get('/')
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'production-devops-platform'

def test_health_returns_200(client): # does /health respond?
    response = client.get('/health')
    assert response.status_code == 200

def test_health_returns_ok(client): # does /health return correct status?
    response = client.get('/health')
    data = response.get_json()
    assert data['status'] == 'ok'

def test_error_returns_500(client): # does /error correctly return 500?
    response = client.get('/error')
    assert response.status_code == 500

def test_metrics_returns_200(client): # does /metrics respond?
    response = client.get('/metrics')
    assert response.status_code == 200