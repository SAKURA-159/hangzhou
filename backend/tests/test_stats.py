def test_get_region_stats(client, sample_houses):
    resp = client.get("/api/stats/regions")
    assert resp.status_code == 200
    data = resp.json()
    assert "regions" in data
    assert len(data["regions"]) == 2  # 西湖, 萧山


def test_get_region_stats_with_filter(client, sample_houses):
    resp = client.get("/api/stats/regions?regions=西湖")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["regions"]) == 1
    assert data["regions"][0]["place"] == "西湖"
    assert data["regions"][0]["count"] == 3


def test_get_overview_stats(client, sample_houses):
    resp = client.get("/api/stats/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_houses"] == 4
    assert data["total_regions"] == 2
    assert data["type_distribution"]["住宅"] == 3
    assert data["type_distribution"]["别墅"] == 1
