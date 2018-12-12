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
    """
    Link create and update form.
    """

    title = StringField("title", validators=[Length(max=300)])
    url = URLField("url", validators=[URL(), Length(max=600), Required()])
    description = TextAreaField("description", validators=[Length(max=1000)])
    tags = TagListField("tags", validators=[Length(max=50)])
    save_a_copy = BooleanField("save page", default=False)
    read_later = BooleanField("read later", default=False)
    is_popup = BooleanField(default=False, widget=HiddenInput())


class LinkFilterForm(FlaskForm):
    tag = StringField()
    domain = URLField()
    read_later = BooleanField()


def render_links_create_form(url, title, is_popup):
    """
    This function renders link create form. This function is called
    from `links_create` function on a GET request. This method is
    split from the `links_create` function because it got a little big
    and for better testability.

    The arguments `url` and `title` are the initial data, they are
    there to auto-fill the respective fields when the form renders.
    This is how the JS bookmarklet works.

    The `url` argument in particular also has another use. That is, if
    a `url` already has an entry in our database, instead of rendering
    the create form, we redirect to the update page for the existing
    entry.

    The `is_popup` argument determines which template to render, the
    full site template or just the form fragment. When we're using the
    bookmarklet, we just want the link create form to render.
    """
    page_title = "adding link"
    if url:
        dupe = find_by_url(url)
        if dupe is not None:
            to = url_for(
                "links.links_update",
                id=dupe["_id"],
                is_popup="y" if is_popup else "n",
            )
            return redirect(to)

    initial = {"url": url, "title": title, "is_popup": is_popup}
    if is_popup:
        template = "form_popup.html"
    else:
        template = "form.html"
        initial = {}
    form = LinkForm(data=initial)
    return render_template(template, form=form, page_title=page_title)


@bp.route("/create/", methods=["POST", "GET"])
def links_create():
    """
    This view function handles creation of a link.
    """
    page_title = "adding link"
    is_popup = request.values.get("is_popup") == "y"

    if request.method == "GET":
        url = request.args.get("url")
        title = request.args.get("title")
        return render_links_create_form(url, title, is_popup)

    # disable csrf for now, to make it easy to test this URL
    form = LinkForm(request.form, meta={"csrf": False})
    if form.validate_on_submit():
        data = process_link_form_data(form.data)
        create_link(**data)
        is_popup = form.data.get("is_popup")

        if is_popup:
            return render_template("close_window.html")
        else:
            return redirect(url_for("links.links"))
    template = "form_popup.html" if is_popup else "form.html"
    return render_template(template, form=form, page_title=page_title), 400


@bp.route("/update/<id>/", methods=["POST", "GET"])
def links_update(id):
    collection = get_db().links
    link = collection.find_one({"_id": ObjectId(id)})

    if not link:
        return "Link not found", 404

    page_title = "updating link"

    if request.method == "GET":
        is_popup = request.args.get("is_popup") is not None
        form = LinkForm(data=link)
        template_name = "form_popup.html" if is_popup else "form.html"
        return render_template(
            template_name, form=form, page_title=page_title, is_update=True
        )

    # disable csrf for now, to make it easy to test this URL
    form = LinkForm(request.form, meta={"csrf": False})
    if form.validate_on_submit():
        data = process_link_form_data(form.data)
        update_link(link, **data)
        is_popup = form.data.get("is_popup")

        if is_popup:
            return render_template("close_window.html")
        else:
            return redirect(url_for("links.links"))
    return (
        render_template(
            "form.html", form=form, page_title=page_title, is_update=True
        ),
        400,
    )


def process_link_form_data(data):
    """
    Remove unwanted fields from the forms
    """
    data.pop("csrf_token", None)
    data.pop("is_popup", None)
    return data


def update_link(link, **kwargs):
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
    kwargs["created_at"] = datetime.now()

    url = kwargs["url"]
    title = kwargs.get("title", "") or url

    prefs = get_preferences()
    if prefs["prepend_pdf_in_title"]:
        if url.endswith(".pdf") and "[PDF]" not in title:
            title = f"[PDF] {title}"

    kwargs["title"] = title
    result = get_db().links.insert_one(kwargs)

    if kwargs.pop("save_a_copy", False):
        make_copy_of_url(kwargs["url"], result.inserted_id)
    return result


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
    query = {}
    if tag:
        query["tags"] = {"$in": [tag]}

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


def find_by_url(url):
    """
    Take a URL and try to return an entry for that url if it exists.
    Returns None if not found. This method is used to find existing
    entry while creating a bookmark to avoid duplicacy.
    """
    links = get_db().links
    link = links.find_one({"url": {"$eq": url}})
    return link


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
