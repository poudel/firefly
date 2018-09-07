import urllib
from datetime import datetime
import humanize
from flask import Blueprint, render_template, request, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import URL, Length, Required
from firefly.db import get_db
from firefly.preferences import get_preferences


bp = Blueprint("links", __name__, url_prefix="/links")


class LinkForm(FlaskForm):
    title = StringField("title", validators=[Length(max=100)])
    url = StringField("url", validators=[URL(), Length(max=500), Required()])
    description = StringField("description", validators=[Length(max=500)])
    tags = StringField(
        "tags separated by space",
        validators=[Length(max=50)],
        description="Space separated",
    )
    make_a_copy = BooleanField("make a copy of the page", default=False)


@bp.route("/create/", methods=["POST", "GET"])
def links_create():
    if request.method == "GET":
        url = request.args.get("url")
        title = request.args.get("title")

        if url or title:
            form = LinkForm(data={"url": url, "title": title})
        else:
            form = LinkForm()
        return render_template("links_form.html", form=form)

    form = LinkForm(request.form)
    if form.validate_on_submit():
        create_link(**form.data)
        return redirect(url_for("links.links"))
    return render_template("links_form.html", form=form)


def create_link(**kwargs):
    make_a_copy = kwargs.pop("make_a_copy")
    del kwargs["csrf_token"]

    tags = map(lambda t: t.strip(), kwargs["tags"].split(" "))
    tags = list(filter(lambda t: bool(t), tags))
    if tags:
        kwargs["tags"] = tags

    kwargs["created_at"] = datetime.now()
    if "title" not in kwargs:
        kwargs["title"] = kwargs["url"]
    get_db().links.insert_one(kwargs)


def delete_link(id):
    get_db().links.find({"_id": id})


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
        link["domain"] = urllib.parse.urlparse(link["url"]).hostname
        data.append(link)
    return data


def paginate_cursor(cursor, page_size, page_num):
    """
    returns a set of documents belonging to page number `page_num`
    where size of each page is `page_size`.

    Copy pasted from: https://www.codementor.io/arpitbhayani/fast-and-efficient-pagination-in-mongodb-9095flbqr
    """
    # Calculate number of documents to skip
    skips = page_size * (page_num - 1)

    # Skip and limit
    return cursor.skip(skips).limit(page_size)


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
        "config": prefs,
        "current_page_num": page_num,
        "next_page_num": page_num + 1 if len(links_qs) == page_size else None,
        "prev_page_num": page_num - 1 if page_num > 1 else None,
        "selected_tag": tag,
    }
    return render_template("links.html", **context)
