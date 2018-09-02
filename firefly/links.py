from flask import Blueprint, render_template


bp = Blueprint("links", __name__, url_prefix="/links")


@bp.route("/")
def links():
    links = [
        {"url": "https://google.com", "title": "Google"},
        {"url": "https://facebook.com", "title": "Facebook"},
        {"url": "https://twitter.com", "title": "Twitter"},
        {"url": "https://instagram.com", "title": "Instagram"},
    ]
    return render_template("links.html", links=links)
