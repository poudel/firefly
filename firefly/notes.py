"""
Notes: save notes, code snippets etc.
"""
from datetime import datetime
import humanize
from markdown2 import markdown
from bson.objectid import ObjectId
from flask import Blueprint, render_template, request, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import Length, Required
from firefly.db import get_db
from firefly.form_fields import TagListField
from firefly.preferences import get_preferences


# pylint: disable=invalid-name
bp = Blueprint("notes", __name__, url_prefix="/notes")


class NoteForm(FlaskForm):
    title = StringField("title", validators=[Length(max=200)])
    tags = TagListField("tags", validators=[Length(max=50)])
    description = TextAreaField("content", validators=[Required()])


@bp.route("/create/", methods=["POST", "GET"])
def notes_create():
    page_title = "adding note"

    if request.method == "GET":
        form = NoteForm()
        return render_template("form.html", form=form, page_title=page_title)

    form = NoteForm(request.form, meta={"csrf": False})
    if form.validate_on_submit():
        result = create_note(**form.data)
        return redirect(url_for("notes.notes_detail", id=result.inserted_id))
    return render_template("form.html", form=form, title=page_title), 400


def create_note(**kwargs):
    kwargs.pop("csrf_token", None)
    kwargs["created_at"] = datetime.now()

    title = kwargs.get("title")
    if not title:
        kwargs["title"] = "untitled"
    return get_db().notes.insert_one(kwargs)


@bp.route("/update/<id>/", methods=["GET", "POST"])
def notes_update(id):
    collection = get_db().notes
    note = collection.find_one({"_id": ObjectId(id)})

    if not note:
        return "Note not found", 404

    page_title = "updating note"

    if request.method == "GET":
        form = NoteForm(data=note)
        return render_template("form.html", form=form, page_title=page_title)

    # disable csrf for now, to make it easy to test this URL
    form = NoteForm(request.form, meta={"csrf": False})
    if form.validate_on_submit():
        update_note(note, **form.data)
        return redirect(url_for("notes.notes_detail", id=id))
    return render_template("form.html", form=form, page_title=page_title), 400


def update_note(note, **kwargs):
    kwargs.pop("csrf_token", None)
    note.update(kwargs)
    get_db().notes.replace_one({"_id": note["_id"]}, note)
    return note


@bp.route("/delete/<id>/", methods=["GET", "POST"])
def notes_delete(id):
    collection = get_db().notes
    note = collection.find_one({"_id": ObjectId(id)})

    if not note:
        return "Note not found", 404

    if request.method == "GET":
        return render_template(
            "confirm_delete.html",
            item=note,
            back_url=url_for("notes.notes"),
            page_title="deleting note",
        )

    collection.remove(note)
    return redirect(url_for("notes.notes"))


def get_notes(tag=None):
    if tag:
        query = {"tags": {"$in": [tag]}}
    else:
        query = {}
    return get_db().notes.find(query).sort("created_at", -1)


def notes_pre_render(notes_queryset):
    data = []

    for note in notes_queryset:
        note["naturaltime"] = humanize.naturaltime(note["created_at"])
        data.append(note)
    return data


@bp.route("/")
def notes():
    tag = request.args.get("tag", None)

    context = {
        "notes": notes_pre_render(get_notes(tag)),
        "prefs": get_preferences(),
    }
    return render_template("notes.html", **context)


@bp.route("/detail/<id>/")
def notes_detail(id):
    collection = get_db().notes
    note = collection.find_one({"_id": ObjectId(id)})

    if not note:
        return "Note not found", 404

    note["html"] = markdown(
        note["description"],
        extras=["fenced-code-blocks", "break-on-newline", "cuddled-lists"],
    )

    return render_template("notes_detail.html", note=note)
