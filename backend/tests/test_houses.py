def test_list_houses(client, sample_houses):
    resp = client.get("/api/houses")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 4
    assert len(data["items"]) == 4


def test_list_houses_pagination(client, sample_houses):
    resp = client.get("/api/houses?page=1&page_size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["total"] == 4
    assert data["total_pages"] == 2


def test_list_houses_filter_region(client, sample_houses):
    resp = client.get("/api/houses?region=西湖")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3


def test_list_houses_filter_property_type(client, sample_houses):
    resp = client.get("/api/houses?property_type=别墅")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1


def test_get_house(client, sample_houses):
    resp = client.get("/api/houses/1")
    assert resp.status_code == 200
    assert resp.json()["name"] == "测试楼盘1"


def test_get_house_not_found(client):
    resp = client.get("/api/houses/999")
    assert resp.status_code == 404


def test_create_house_admin(client, admin_token_headers):
    resp = client.post("/api/houses", json={
        "name": "新楼盘", "place": "余杭", "price": 25000.0,
    }, headers=admin_token_headers)
    assert resp.status_code == 201
    assert resp.json()["name"] == "新楼盘"


def test_create_house_unauthorized(client):
    resp = client.post("/api/houses", json={
        "name": "未授权", "place": "测试", "price": 10000.0,
    })
    assert resp.status_code == 401


def test_create_house_non_admin(client, user_token_headers):
    resp = client.post("/api/houses", json={
        "name": "非管理员", "place": "测试", "price": 10000.0,
    }, headers=user_token_headers)
    assert resp.status_code == 403


def test_update_house(client, admin_token_headers, sample_houses):
    resp = client.put("/api/houses/1", json={
        "price": 55000.0,
    }, headers=admin_token_headers)
    assert resp.status_code == 200
    assert resp.json()["price"] == 55000.0


def test_delete_house(client, admin_token_headers, sample_houses):
    resp = client.delete("/api/houses/1", headers=admin_token_headers)
    assert resp.status_code == 200
    assert resp.json()["message"] == "House deleted successfully"


def test_search_houses(client, sample_houses):
    resp = client.get("/api/houses?search=别墅")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
