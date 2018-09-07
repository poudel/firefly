from flask import Blueprint, render_template


bp = Blueprint("views", __name__, url_prefix="/views")


@bp.route("/tools/")
def tools():
    return render_template("tools.html")
