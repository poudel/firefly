from datetime import datetime
from firefly.db import get_db
from firefly.links import get_links


def test_get_links_adds_naturaltime(app):
    links = get_db().links
    links.insert_one(
        {"url": "https://google.com", "created_at": datetime(2018, 1, 1, 0, 0, 0)}
    )

    saved_links = get_links()
    assert len(saved_links) == 1
    assert "naturaltime" in saved_links[0]


def test_links_view(client):
    res = client.get("/links/")
    assert res.status_code == 200
