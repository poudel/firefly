from flask import Blueprint, render_template


bp = Blueprint("links", __name__, url_prefix="/links")


def update_defaults(l):
    link = {"new_tab": True}
    link.update(l)
    return link


@bp.route("/")
def links():

    links = [
        {"url": "https://google.com", "title": "Google", "new_tab": False},
        {"url": "https://facebook.com", "title": "Facebook"},
        {"url": "https://twitter.com", "title": "Twitter"},
        {"url": "https://instagram.com", "title": "Instagram"},
    ]
    return render_template("links.html", links=map(update_defaults, links))
