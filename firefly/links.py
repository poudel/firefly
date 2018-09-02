from flask import Blueprint, render_template


bp = Blueprint("links", __name__, url_prefix="/links")


@bp.route("/")
def links():
    return render_template("links.html")
