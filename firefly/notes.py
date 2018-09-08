"""
Notes: save notes, code snippets etc.
"""
from datetime import datetime
from flask import Blueprint, render_template, request, url_for, redirect
import humanize
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField
from wtforms.validators import URL, Length, Required
from firefly.form_fields import TagListField


# pylint: disable=invalid-name
bp = Blueprint("notes", __name__, url_prefix="/notes")


class NoteForm(FlaskForm):
    title = StringField("title", validators=[Length(max=200)])
    content = TextAreaField("content")
    tags = TagListField(
        "tags separated by space",
        validators=[Length(max=50)],
        description="Space separated",
    )


@bp.route("/create/", methods=["POST", "GET"])
def notes_create():
    page_title = "adding note"

    if request.method == "GET":
        form = NoteForm()
        return render_template("form.html", form=form, page_title=page_title)

    form = NoteForm(request.form, meta={"csrf": False})
    if form.validate_on_submit():
        create_note(**form.data)
        return redirect(url_for("notes.notes"))
    return render_template("form.html", form=form, title=page_title), 400


def create_note(**kwargs):
    kwargs.pop("csrf_token", None)
    kwargs["created_at"] = datetime.now()

    if "title" not in kwargs:
        kwargs["title"] = "Untitled note"
    get_db().notes.insert_one(**kwargs)


@bp.route("/")
def notes():
    return render_template("notes.html")


@bp.route("/detail/<id>/")
def notes_detail(id):
    return render_template("notes_detail.html")
