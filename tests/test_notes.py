from datetime import datetime
import pytest
from bson.objectid import ObjectId
from firefly.db import get_db
from firefly.notes import get_notes, notes_pre_render, create_note


@pytest.fixture
def onenote():
    return {
        "title": "example.py",
        "description": "lambda x: x",
        "tags": "python lambda",
    }


def test_notes_create_get(client):
    res = client.get("/notes/create/")
    assert res.status_code == 200


def test_notes_create_post_is_creating(client, onenote):
    onenote["title"] = "creation"

    res = client.post("/notes/create/", data=onenote)
    assert res.status_code == 302

    fetched = list(get_db().notes.find())[0]
    assert fetched["title"] == "creation"


def test_create_note(app, onenote):
    create_note(**onenote)

    fetched = list(get_db().notes.find())[0]
    assert "csrf_token" not in fetched, "should exclude csrf_token"
    assert "created_at" in fetched, "should add created_at"


def test_create_note_puts_untitled_in_if_title_is_not_provided(app, onenote):
    onenote.pop("title")
    create_note(**onenote)

    fetched = list(get_db().notes.find())[0]
    assert fetched["title"] == "untitled"


def test_notes_update_get_invalid_url(client):
    id = ObjectId("5b92b2cd5e378f694898087b")
    res = client.get(f"/notes/update/{id}/")
    assert res.status_code == 404


def test_notes_update_get_valid_url(client, onenote):
    id = ObjectId("5b92b2cd5e378f694898087c")
    create_note(_id=ObjectId(id), **onenote)

    res = client.get(f"/notes/update/{id}/")
    assert res.status_code == 200


def test_notes_update_post(client, onenote):
    id = ObjectId("5b92b2cd5e378f694898087d")
    create_note(_id=ObjectId(id), **onenote)

    onenote["title"] = "random_title"
    res = client.post(f"/notes/update/{id}/", data=onenote)
    assert res.status_code == 302

    fetched = get_db().notes.find_one({"_id": id})
    assert fetched["title"] == "random_title"


def test_notes_delete_get_with_invalid_id(client):
    id = ObjectId("5b92b2cd5e378f694898087a")
    res = client.get(f"/notes/delete/{id}/")
    assert res.status_code == 404


def test_notes_delete_get_with_valid_id(client, onenote):
    id = ObjectId("5b92b2cd5e378f694898087a")
    create_note(_id=ObjectId(id), **onenote)

    res = client.get(f"/notes/delete/{id}/")
    assert res.status_code == 200


def test_notes_delete_post(client, onenote):
    id = ObjectId("5b92b2cd5e378f694898087a")
    create_note(_id=ObjectId(id), **onenote)

    res = client.post(f"/notes/delete/{id}/")
    assert res.status_code == 302
    assert not get_db().notes.find_one({"_id": id})


@pytest.fixture
def save_notes(app):
    notes = get_db().notes
    notes.insert_many(
        [
            {
                "title": "something.md",
                "description": "hello world",
                "created_at": datetime(2018, 1, 1, 0, 0, 0),
                "tags": ["tag1", "tag2"],
            },
            {
                "title": "anything.md",
                "description": "any world",
                "created_at": datetime(2018, 1, 1, 0, 0, 0),
                "tags": ["tag3", "tag2"],
            },
        ]
    )


def test_get_notes_without_tag_argument(save_notes):
    all_notes = list(get_notes())
    assert len(all_notes) == 2


def test_get_notes_with_tag_argument(save_notes):
    tag1 = list(get_notes("tag1"))
    assert len(tag1) == 1
    assert "tag1" in tag1[0]["tags"]

    tag2 = list(get_notes("tag2"))
    assert len(tag2) == 2
    assert "tag2" in tag2[0]["tags"]


def test_notes_pre_render(app, save_notes):
    fetched_notes = notes_pre_render(get_notes())

    assert len(fetched_notes) == 2

    note1, note2 = fetched_notes
    assert "naturaltime" in note1
    assert "naturaltime" in note2


def test_notes_view(client):
    res = client.get("/notes/")
    assert res.status_code == 200
