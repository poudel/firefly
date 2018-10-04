from urllib import parse
from datetime import datetime
import pytest
from bson.objectid import ObjectId
from firefly.db import get_db
from firefly.preferences import get_preferences, update_preferences
from firefly.links import (
    get_links,
    links_pre_render,
    create_link,
    update_link,
    delete_link,
    get_tags,
    remove_ref_query_param,
    process_link_form_data,
)


@pytest.fixture
def onelink():
    return {
        "title": "Example",
        "url": "https://example.com",
        "description": "A search engine",
        "tags": "search alphabet",
        "save_a_copy": False,  # set this to False to avoid running the crawler
    }


def test_links_create_get(client):
    res = client.get("/links/create/")
    assert res.status_code == 200


def test_links_create_post_is_creating(client, db, onelink):
    onelink["title"] = "creation"
    onelink["save_a_copy"] = None

    res = client.post("/links/create/", data=onelink)
    assert res.status_code == 302

    fetched = db.links.find_one()
    assert fetched["title"] == "creation"


def test_create_link(app, db, onelink):
    create_link(**onelink)

    fetched = db.links.find_one()
    assert "csrf_token" not in fetched, "should exclude csrf_token"
    assert "created_at" in fetched, "should add created_at"


@pytest.fixture
def mock_make_copy():
    class Make:
        def __call__(self, url, link_id):
            self.url = url
            self.link_id = link_id

    return Make()


def test_create_link_on_save_a_copy(app, onelink, monkeypatch, mock_make_copy):
    onelink["save_a_copy"] = True
    monkeypatch.setattr("firefly.links.make_copy_of_url", mock_make_copy)
    create_link(**onelink)

    assert mock_make_copy.url == onelink["url"]
    assert mock_make_copy.link_id


def test_create_link_puts_pdf_prefix_if_enabled_in_prefs(app, db, onelink):
    # this creates a default preferences
    get_preferences()
    update_preferences(prepend_pdf_in_title=True)

    onelink["url"] = "https://example.com/sample.pdf"
    create_link(**onelink)

    fetched = db.links.find_one()
    assert fetched["title"].startswith("[PDF] ")
    assert fetched["title"] == "[PDF] " + onelink["title"]


def test_create_link_doesnt_put_pdf_prefix_if_disabled_in_prefs(db, onelink):
    # this creates a default preferences
    get_preferences()
    update_preferences(prepend_pdf_in_title=False)

    onelink["url"] = "https://example.com/sample.pdf"
    create_link(**onelink)

    fetched = db.links.find_one()
    assert not fetched["title"].startswith("[PDF] ")


def test_create_link_puts_url_in_if_title_is_not_provided(db, onelink):
    onelink.pop("title")
    result = create_link(**onelink)

    fetched = db.links.find_one(result.inserted_id)
    assert fetched["title"] == onelink["url"]


@pytest.mark.parametrize("ref_key", ["ref", "ref_", "_ref"])
def test_remove_ref_query_param_removes_ref_query_param(ref_key):
    url = f"https://www.imdb.com/title/tt4378376/?{ref_key}=tt_rec_tt"
    new_url = remove_ref_query_param(url)
    assert new_url == "https://www.imdb.com/title/tt4378376/"


def test_remove_ref_query_param_retains_other_params():
    url = "https://hello.com/?ref=asdf&jaja=kaka&nana=mama"
    new_url = remove_ref_query_param(url)
    parsed = parse.urlparse(new_url)
    assert parse.parse_qs(parsed.query) == {"jaja": ["kaka"], "nana": ["mama"]}


def test_links_update_get_invalid_url(client):
    id = ObjectId("5b92b2cd5e378f694898087b")
    res = client.get(f"/links/update/{id}/")
    assert res.status_code == 404


def test_links_update_get_valid_url(client, onelink):
    id = ObjectId("5b92b2cd5e378f694898087c")
    create_link(_id=ObjectId(id), **onelink)

    res = client.get(f"/links/update/{id}/")
    assert res.status_code == 200


def test_links_update_post(client, db, onelink):
    id = ObjectId("5b92b2cd5e378f694898087d")
    create_link(_id=ObjectId(id), **onelink)

    onelink["url"] = "https://google.com/asdf/"
    res = client.post(f"/links/update/{id}/", data=onelink)
    assert res.status_code == 302

    fetched = db.links.find_one({"_id": id})
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


def test_links_delete_post(client, db, onelink):
    id = ObjectId("5b92b2cd5e378f694898087a")
    create_link(_id=ObjectId(id), **onelink)

    res = client.post(f"/links/delete/{id}/")
    assert res.status_code == 302
    assert not db.links.find_one({"_id": id})


@pytest.fixture
def save_links(db):
    links = db.links
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


def test_process_link_form_data():
    form_data = {"title": "Hello", "csrf_token": "asfddf", "close_window": True}
    processed_data = process_link_form_data(form_data)
    assert "csrf_token" not in processed_data
    assert "close_window" not in processed_data


def test_update_link(db, onelink):
    result = create_link(**onelink)

    link = db.links.find_one(result.inserted_id)

    return_link = update_link(link, title="Updated example")
    assert isinstance(return_link, dict)
    assert link["_id"] == return_link["_id"]
    assert link["title"] == "Updated example"

    db_link = db.links.find_one(result.inserted_id)
    assert db_link["title"] == "Updated example"
