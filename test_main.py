from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_readers():
    response = client.get("/readers", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjNAbWFpbC5ydSJ9.fm5xx8I3sUex5e89tCoA8CRPeHQSV3uEIRT-aYrx2Hk"})
    assert response.status_code == 200

def test_readers2():
    response = client.get("/readers")
    assert response.status_code == 401
