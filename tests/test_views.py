def test_tools_renders(client):
    res = client.get("/views/tools/")
    assert res.status_code == 200
