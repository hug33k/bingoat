from fastapi.testclient import TestClient
from ..misc import router


client = TestClient(router)


def test_get_status():
    response = client.get("/status")
    data = response.json()
    assert response.status_code == 200
    assert type(data) == dict
    assert "status" in data
    assert data["status"] == True
    assert "date" in data
    assert type(data["date"]) == str
