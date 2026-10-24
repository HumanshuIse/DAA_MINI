from app import create_app
from database.db import Database


def test_api(tmp_path):
    app = create_app({"TESTING": True, "DB": Database(tmp_path / "test.sqlite3")})
    client = app.test_client()
    assert client.get("/api/health").json["status"] == "ok"
    assert client.post("/api/sort/trace", json={"array": [3, 1, 2]}).json["sorted"] == [1, 2, 3]
    assert client.post("/api/sort/trace", json={"array": ["bad"]}).status_code == 400
    response = client.post("/api/benchmark", json={"size": 32, "repetitions": 1})
    assert response.status_code == 200
    assert client.get("/api/benchmark/history").json["items"]
    assert client.get("/api/benchmark/export").status_code == 200
