from urllib.parse import urljoin
from flask import Blueprint, render_template, request, url_for


bp = Blueprint("views", __name__, url_prefix="/views")


@bp.route("/tools/")
def tools():
    create_url = urljoin(request.url_root, url_for("links.links_create"))
    return render_template("tools.html", create_url=create_url)
