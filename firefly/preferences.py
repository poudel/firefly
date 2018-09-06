from flask import Blueprint, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField
from firefly.db import get_db
from firefly.form_utils import get_form_defaults


bp = Blueprint("preferences", __name__, url_prefix="/preferences")


class PreferenceForm(FlaskForm):
    show_target_link = BooleanField(
        "Show target link below bookmark title", default=True
    )
    make_target_link_clickable = BooleanField("Also make it clickable", default=True)
    show_target_domain = BooleanField(
        "Show target domain (inside parenthesis)", default=True
    )
    open_new_tab = BooleanField("Open bookmarked links in new tab", default=True)
    show_copy_link = BooleanField(
        "Display 'copy' button (copies the URL to clipboard)", default=True
    )
    show_cached_link = BooleanField(
        "Display 'cached' button (redirects to a cached version)", default=True
    )
    show_archived_link = BooleanField(
        "Show a link to archive sites such as archive.is", default=True
    )
    archive_link_format = StringField(
        "Format for archive URL", default="https://archive.is/{url}"
    )
    timezone = StringField("Your timezone", default="Asia/Kathmandu")


def get_defaults():
    return get_form_defaults(PreferenceForm)


def get_preferences():
    config = get_db().preferences.find_one("1")
    if not config:
        return create_defaults()
    return config


def create_defaults():
    defaults = get_defaults()
    defaults["_id"] = "1"
    get_db().preferences.insert_one(defaults)
    return defaults


# pylint: disable=invalid-name
def update_defaults():
    defaults = get_defaults()
    config = get_preferences()

    updated = {}
    # insert newly added config keys
    for k, v in defaults.items():
        if k not in config:
            updated[k] = v

    # remove stale config keys
    for k, v in config.copy().items():
        if k == "_id":
            continue

        if k not in defaults:
            del config[k]

    config.update(updated)
    get_db().preferences.replace_one({"_id": config["_id"]}, config)


def update_preferences(**kwargs):
    """
    Can be used to update preferences
    """
    pref = get_preferences()

    for k, v in kwargs.items():
        if k in pref:
            pref[k] = v

    get_db().preferences.replace_one({"_id": pref["_id"]}, pref)


@bp.route("/", methods=["GET", "POST"])
def preferences():
    if request.method == "GET":
        pref = get_preferences()
        form = PreferenceForm(data=pref)
        return render_template("preferences.html", form=form)

    form = PreferenceForm(request.form)
    if form.validate_on_submit():
        update_preferences(**form.data)
        return redirect(url_for("preferences.preferences"))
    return render_template("preferences.html", form=form)
