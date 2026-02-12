import jwt
import time
import pytest
from app.core.security import SECRET_KEY, ALGORITHM
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_missing_claims():
    token = jwt.encode({'sub': 'user'}, SECRET_KEY, algorithm=ALGORITHM)
    response = client.get('/api/v1/services', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 401

def test_invalid_issuer():
    token = jwt.encode({'sub': 'user', 'iss': 'wrong', 'aud': 'resilienceops-users', 'exp': int(time.time())+3600}, SECRET_KEY, algorithm=ALGORITHM)
    response = client.get('/api/v1/services', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 401

def test_expired_token():
    token = jwt.encode({'sub': 'user', 'iss': 'resilienceops', 'aud': 'resilienceops-users', 'exp': int(time.time())-3600}, SECRET_KEY, algorithm=ALGORITHM)
    response = client.get('/api/v1/services', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 401

def test_missing_role_viewer_cannot_post():
    token = jwt.encode({'sub': 'user', 'iss': 'resilienceops', 'aud': 'resilienceops-users', 'exp': int(time.time())+3600, 'roles': ['viewer']}, SECRET_KEY, algorithm=ALGORITHM)
    response = client.post('/api/v1/services', json={'name': 'test_viewer', 'version': '1.0'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 403

def test_valid_role_operator_can_post():
    token = jwt.encode({'sub': 'user', 'iss': 'resilienceops', 'aud': 'resilienceops-users', 'exp': int(time.time())+3600, 'roles': ['operator']}, SECRET_KEY, algorithm=ALGORITHM)
    response = client.post('/api/v1/services', json={'name': 'test_operator', 'version': '1.0'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    
def test_viewer_can_get():
    token = jwt.encode({'sub': 'user', 'iss': 'resilienceops', 'aud': 'resilienceops-users', 'exp': int(time.time())+3600, 'roles': ['viewer']}, SECRET_KEY, algorithm=ALGORITHM)
    response = client.get('/api/v1/services', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200

def test_production_dev_token_rejected(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'production')
    monkeypatch.setenv('SECRET_KEY', 'testsecret')
    response = client.get('/api/v1/services', headers={'Authorization': 'Bearer dev-token'})
    assert response.status_code == 401

def test_missing_secret_key_in_production(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'production')
    monkeypatch.delenv('SECRET_KEY', raising=False)
    
    import importlib
    import app.core.security as security
    
    with pytest.raises(RuntimeError, match="SECRET_KEY environment variable is required in production"):
        importlib.reload(security)
