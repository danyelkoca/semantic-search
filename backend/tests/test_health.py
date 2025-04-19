from dotenv import load_dotenv
from fastapi.testclient import TestClient

from backend.main import app

load_dotenv()


client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("ok") is True
