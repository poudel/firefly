from flask import Blueprint, render_template
from firefly.db import get_db
from firefly.preferences import get_preferences


bp = Blueprint("links", __name__, url_prefix="/links")


@bp.route("/create/", methods=["POST", "GET"])
def links_create():
    return render_template("links_form.html")


@bp.route("/")
def links():
    context = {"links": get_db().links.find(), "config": get_preferences()}
    return render_template("links.html", **context)
