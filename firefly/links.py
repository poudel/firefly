from urllib import parse
from datetime import datetime
import humanize
from bson.objectid import ObjectId
from flask import Blueprint, render_template, request, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField
from wtforms.fields.html5 import URLField
from wtforms.widgets import HiddenInput
from wtforms.validators import URL, Length, Required

from firefly.db import get_db
from firefly.preferences import get_preferences
from firefly.helpers import paginate_cursor
from firefly.form_fields import TagListField
from firefly.archive import save_file


# pylint: disable=invalid-name
bp = Blueprint("links", __name__, url_prefix="/links")


class LinkForm(FlaskForm):
    title = StringField("title", validators=[Length(max=300)])
    url = URLField("url", validators=[URL(), Length(max=600), Required()])
    description = TextAreaField("description", validators=[Length(max=1000)])
    tags = TagListField(
        "tags",
        validators=[Length(max=50)],
        description="Space separated list of tags",
    )
    save_a_copy = BooleanField("save page", default=False)
    close_window = BooleanField(
        "close on save",
        default=False,
        description="try to close the window after saving the bookmark",
        widget=HiddenInput(),
    )


@bp.route("/create/", methods=["POST", "GET"])
def links_create():
    page_title = "adding link"
    if request.method == "GET":
        url = request.args.get("url")
        title = request.args.get("title")

        if url or title:
            initial = {"url": url, "title": title, "close_window": True}
            form = LinkForm(data=initial)
            return render_template(
                "form_popup.html", form=form, page_title=page_title
            )
        else:
            form = LinkForm()
            return render_template(
                "form.html", form=form, page_title=page_title
            )

    # disable csrf for now, to make it easy to test this URL
    form = LinkForm(request.form, meta={"csrf": False})
    if form.validate_on_submit():
        create_link(**form.data)

        if form.data["close_window"]:
            return render_template("close_window.html")
        else:
            return redirect(url_for("links.links"))
    return render_template("form.html", form=form, page_title=page_title), 400


@bp.route("/update/<id>/", methods=["POST", "GET"])
def links_update(id):
    collection = get_db().links
    link = collection.find_one({"_id": ObjectId(id)})

    if not link:
        return "Link not found", 404

    page_title = "updating link"

    if request.method == "GET":
        form = LinkForm(data=link)
        return render_template("form.html", form=form, page_title=page_title)

    # disable csrf for now, to make it easy to test this URL
    form = LinkForm(request.form, meta={"csrf": False})
    if form.validate_on_submit():
        update_link(link, **form.data)
        return redirect(url_for("links.links"))
    return render_template("form.html", form=form, page_title=page_title), 400


def update_link(link, **kwargs):
    kwargs.pop("csrf_token", None)
    link.update(kwargs)
    get_db().links.replace_one({"_id": link["_id"]}, link)
    return link


def make_copy_of_url(url, link_id):
    """
    Save a url
    """
    file_id = save_file(url, link_id)

    get_db().links.update_one(
        {"_id": ObjectId(link_id)}, {"$set": {"saved_file": file_id}}
    )


def create_link(**kwargs):
    kwargs.pop("csrf_token", None)
    kwargs.pop("close_window", None)
    kwargs["created_at"] = datetime.now()

    url = kwargs["url"].lower()
    title = kwargs.get("title", url)

    prefs = get_preferences()
    if prefs["prepend_pdf_in_title"]:
        if url.endswith(".pdf") and "[PDF]" not in title:
            title = f"[PDF] {title}"

    if prefs["remove_ref_query_param"]:
        kwargs["url"] = remove_ref_query_param(url)

    kwargs["title"] = title
    result = get_db().links.insert_one(kwargs)

    if kwargs.pop("save_a_copy", False):
        make_copy_of_url(kwargs["url"], result.inserted_id)


def remove_ref_query_param(url):
    parsed = parse.urlparse(url)

    query_params = parse.parse_qs(parsed.query)

    for key in ["ref", "ref_", "_ref"]:
        query_params.pop(key, None)

    # since parse_qs makes a=b -> {'a': ['b']}, we provide doseq=True
    # to parse it likewise
    querystr = parse.urlencode(query_params, doseq=True)
    new_url = list(parsed)
    new_url[4] = querystr
    return parse.urlunparse(new_url)


@bp.route("/delete/<id>/", methods=["GET", "POST"])
def links_delete(id):
    """
    View to delete link
    """
    collection = get_db().links
    link = collection.find_one({"_id": ObjectId(id)})

    if not link:
        return "Link not found", 404

    if request.method == "GET":
        return render_template(
            "confirm_delete.html",
            item=link,
            back_url=url_for("links.links"),
            page_title="deleting link",
        )

    collection.remove(link)
    return redirect(url_for("links.links"))


def delete_link(id):
    if not isinstance(id, ObjectId):
        id = ObjectId(id)

    return get_db().links.delete_one({"_id": id})


def get_links(tag=None):
    if tag:
        query = {"tags": {"$in": [tag]}}
    else:
        query = {}
    return get_db().links.find(query).sort("created_at", -1)


def links_pre_render(links_queryset):
    data = []

    for link in links_queryset:
        link["naturaltime"] = humanize.naturaltime(link["created_at"])
        link["domain"] = parse.urlparse(link["url"]).hostname
        data.append(link)
    return data


def get_tags():
    return get_db().links.distinct("tags")


@bp.route("/")
def links():
    page_num = int(request.args.get("page", 1))
    tag = request.args.get("tag", None)

    prefs = get_preferences()
    page_size = prefs["page_size"]
    links_qs = links_pre_render(
        paginate_cursor(get_links(tag=tag), page_size, page_num)
    )
    context = {
        "links": links_qs,
        "current_page_num": page_num,
        "next_page_num": page_num + 1 if len(links_qs) == page_size else None,
        "prev_page_num": page_num - 1 if page_num > 1 else None,
        "selected_tag": tag,
        "tags": get_tags(),
    }
    return render_template("links.html", **context)
