def test_links_view(client):
    res = client.get("/links/")
    assert res.status_code == 200
