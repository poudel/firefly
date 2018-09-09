from datetime import datetime
import pytest
from bson.objectid import ObjectId
from firefly.db import get_db
from firefly.links import (
    get_links,
    links_pre_render,
    create_link,
    delete_link,
    get_tags,
)


@pytest.fixture
def onelink():
    return {
        "title": "Example",
        "url": "https://example.com",
        "description": "A search engine",
        "tags": "search alphabet",
        "make_a_copy": True,
    }


def test_links_create_get(client):
    res = client.get("/links/create/")
    assert res.status_code == 200


def test_links_create_post_is_creating(client, onelink):
    onelink["title"] = "creation"

    res = client.post("/links/create/", data=onelink)
    assert res.status_code == 302

    fetched = list(get_db().links.find())[0]
    assert fetched["title"] == "creation"


def test_create_link(app, onelink):
    create_link(**onelink)

    fetched = list(get_db().links.find())[0]
    assert "csrf_token" not in fetched, "should exclude csrf_token"
    assert "created_at" in fetched, "should add created_at"


def test_create_link_puts_url_in_if_title_is_not_provided(app, onelink):
    onelink.pop("title")
    create_link(**onelink)

    fetched = list(get_db().links.find())[0]
    assert fetched["title"] == onelink["url"]


def test_links_update_get_invalid_url(client):
    id = ObjectId("5b92b2cd5e378f694898087b")
    res = client.get(f"/links/update/{id}/")
    assert res.status_code == 404


def test_links_update_get_valid_url(client, onelink):
    id = ObjectId("5b92b2cd5e378f694898087c")
    create_link(_id=ObjectId(id), **onelink)

    res = client.get(f"/links/update/{id}/")
    assert res.status_code == 200


def test_links_update_post(client, onelink):
    id = ObjectId("5b92b2cd5e378f694898087d")
    create_link(_id=ObjectId(id), **onelink)

    onelink["url"] = "https://google.com/asdf/"
    res = client.post(f"/links/update/{id}/", data=onelink)
    assert res.status_code == 302

    fetched = get_db().links.find_one({"_id": id})
    assert fetched["url"] == "https://google.com/asdf/"


def test_delete_link(client, onelink):
    id = ObjectId("5b92b2cd5e378f694898087a")
    create_link(_id=ObjectId(id), **onelink)

    res = delete_link(id)
    assert res.deleted_count == 1


def test_links_delete_get_with_invalid_id(client):
    id = ObjectId("5b92b2cd5e378f694898087a")
    res = client.get(f"/links/delete/{id}/")
    assert res.status_code == 404


def test_links_delete_get_with_valid_id(client, onelink):
    id = ObjectId("5b92b2cd5e378f694898087a")
    create_link(_id=ObjectId(id), **onelink)

    res = client.get(f"/links/delete/{id}/")
    assert res.status_code == 200


def test_links_delete_post(client, onelink):
    id = ObjectId("5b92b2cd5e378f694898087a")
    create_link(_id=ObjectId(id), **onelink)

    res = client.post(f"/links/delete/{id}/")
    assert res.status_code == 302
    assert not get_db().links.find_one({"_id": id})


@pytest.fixture
def save_links(app):
    links = get_db().links
    links.insert_many(
        [
            {
                "url": "https://example.com",
                "created_at": datetime(2018, 1, 1, 0, 0, 0),
                "tags": ["tag1", "tag2"],
            },
            {
                "url": "https://www.example1.com",
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


def test_links_pre_render(app, save_links):
    fetched_links = links_pre_render(get_links())

    assert len(fetched_links) == 2

    google, linkedin = fetched_links

    assert "naturaltime" in google
    assert google["domain"] == "example.com"
    assert linkedin["domain"] == "www.example1.com"


def test_get_tags(app, save_links):
    tags = get_tags()
    assert len(tags) == 3
    assert "tag1" in tags
    assert "tag2" in tags
    assert "tag3" in tags


def test_links_view(client):
    res = client.get("/links/")
    assert res.status_code == 200
