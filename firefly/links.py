import humanize
from flask import Blueprint, render_template
from firefly.db import get_db
from firefly.preferences import get_preferences


bp = Blueprint("links", __name__, url_prefix="/links")


@bp.route("/create/", methods=["POST", "GET"])
def links_create():
    return render_template("links_form.html")


def get_links(tag=None):
    if tag:
        query = {"tags": {"$in": [tag]}}
    else:
        query = {}

    return get_db().links.find(query)


def links_pre_render(links_queryset):
    data = []

    for link in links_queryset:
        link["naturaltime"] = humanize.naturaltime(link["created_at"])
        data.append(link)
    return data


@bp.route("/")
@bp.route("/<tag>/")
def links(tag=None):
    links_qs = links_pre_render(get_links(tag=tag))
    context = {"links": links_qs, "config": get_preferences()}
    return render_template("links.html", **context)
