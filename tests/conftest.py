import os
os.environ["DATABASE_URL"] = "sqlite:///./test_voting.db"
os.environ["JWT_SECRET"] = "test-secret"
import pytest
from fastapi.testclient import TestClient
from app.database import Base, engine
from app.main import app

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def client():
    with TestClient(app) as test_client: yield test_client

@pytest.fixture
def auth(client):
    response = client.post("/auth/token", data={"username": "admin", "password": "admin123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

