import pytest
import firefly.preferences
from firefly.preferences import (
    get_defaults,
    get_preferences,
    create_defaults,
    update_defaults,
)
from firefly.db import get_db


def test_get_defaults():
    prefs = get_defaults()
    assert len(prefs) == 8
    assert isinstance(prefs, dict)


def test_get_preferences(app):
    prefs = get_preferences()
    assert isinstance(prefs, dict)


def test_create_defaults(app):
    db = get_db()
    assert not list(db.preferences.find())
    create_defaults()

    saved_prefs = list(db.preferences.find())
    assert saved_prefs
    assert len(saved_prefs)
    assert saved_prefs[0]["_id"] == "1"


@pytest.fixture
def mocked_get_defaults(app):
    defaults = get_defaults()
    stale_key = defaults.keys()[0]
    defaults.pop(stale_key)
    return defaults


def test_update_defaults_removes_stale_pref_key(app, monkeypatch):
    create_defaults()

    defaults = get_defaults()
    stale_key = list(defaults)[0]
    defaults.pop(stale_key)
    monkeypatch.setattr(firefly.preferences, "get_defaults", lambda: defaults)

    update_defaults()

    saved_config = get_db().preferences.find_one("1")
    assert stale_key not in saved_config


def test_update_defaults_adds_new_pref_key(app, monkeypatch):
    create_defaults()

    new_key = "new_key_yay"
    defaults = get_defaults()
    defaults[new_key] = "new_value"
    monkeypatch.setattr(firefly.preferences, "get_defaults", lambda: defaults)

    update_defaults()

    saved_config = get_db().preferences.find_one("1")
    assert new_key in saved_config
    assert saved_config[new_key] == "new_value"


def test_update_defaults_leaves_unchanged_keys_intact(app, monkeypatch):
    create_defaults()

    new_key = "new_key_yay"
    defaults = get_defaults()
    defaults[new_key] = "new_value"
    monkeypatch.setattr(firefly.preferences, "get_defaults", lambda: defaults)

    update_defaults()

    saved_config = get_db().preferences.find_one("1")
    saved_config.pop("_id")
    assert len(saved_config) == len(defaults)
    assert len(set(saved_config).intersection(defaults)) == len(defaults)
