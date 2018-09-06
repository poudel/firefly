import pytest
from datetime import datetime
from firefly.db import get_db
from firefly.links import get_links, links_pre_render


def test_links_pre_render_adds_naturaltime(app):
    links = get_db().links
    links.insert_one(
        {"url": "https://google.com", "created_at": datetime(2018, 1, 1, 0, 0, 0)}
    )

    saved_links = links_pre_render(get_links())
    assert len(saved_links) == 1
    assert "naturaltime" in saved_links[0]


@pytest.fixture
def save_links(app):
    links = get_db().links
    links.insert_many(
        [
            {
                "url": "https://google.com",
                "created_at": datetime(2018, 1, 1, 0, 0, 0),
                "tags": ["tag1", "tag2"],
            },
            {
                "url": "https://linkedin.com",
                "created_at": datetime(2018, 1, 1, 0, 0, 0),
                "tags": ["tag3", "tag2"],
            },
        ]
    )


def test_get_links_without_tag_argument(save_links):
    all_links = list(get_links())
    assert len(all_links) == 2


def test_get_links_with_tag_argument(save_links):
    tag1 = list(get_links("tag1"))
    assert len(tag1) == 1
    assert "tag1" in tag1[0]["tags"]

    tag2 = list(get_links("tag2"))
    assert len(tag2) == 2
    assert "tag2" in tag2[0]["tags"]


def test_links_view(client):
    res = client.get("/links/")
    assert res.status_code == 200
