from io import BytesIO


def test_import_csv(client, admin_token_headers):
    csv_content = b"House name,House place,House price,property_type\r\n\xe5\xaf\xbc\xe5\x85\xa5\xe6\xa5\xbc\xe7\x9b\x98,\xe8\xa5\xbf\xe6\xb9\x96,35000,\xe4\xbd\x8f\xe5\xae\x85\r\n"
    # Above is "导入楼盘,西湖,35000,住宅" in UTF-8
    files = {"file": ("test.csv", BytesIO(csv_content), "text/csv")}
    resp = client.post("/api/import/csv", files=files, headers=admin_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["imported"] >= 1


def test_import_csv_unauthorized(client):
    csv_content = b"House name,House place,House price\r\ntest,test,10000\r\n"
    files = {"file": ("test.csv", BytesIO(csv_content), "text/csv")}
    resp = client.post("/api/import/csv", files=files)
    assert resp.status_code == 401


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
