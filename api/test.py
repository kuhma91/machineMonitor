from fastapi.testclient import TestClient
from machineMonitor.api.main import app

client = TestClient(app)

AUTH_HEADER = {
    "Authorization": "Bearer 57855dd06eddeccb87970a9e739a6da66e1f00826ca33ac392fb3bcbceb33e51"
}


def testPostMachine():
    payload = {
        'tableType': 'machines',
        "name": "testMachine",
        "sector": "Z1",
        "serial_number": "00001",
        "manufacturer": "testMaker",
        "usage": "test",
        "year_of_acquisition": 2024,
        "in_service": True,
        "comment": "test machine"
    }
    response = client.post("/create", params=payload)
    assert response.status_code == 404


def testGetMachineByName():
    response = client.get("/ask?name=testMachine&dataType=machines", headers=AUTH_HEADER)
    assert response.status_code == 200
    result = response.json()
    assert any(m["name"] == "testMachine" for m in result)


def testGetLogsLikeUser():
    response = client.get("/ask?like[userName]=angiu&dataType=logs", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert all("angiu" in log["userName"] for log in response.json())


def testSecureLogsRequiresToken():
    response = client.get("/ask")  # no token
    assert response.status_code == 403
