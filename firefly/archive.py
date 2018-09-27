import mimetypes
import gridfs
from requests_html import HTMLSession
from bson.objectid import ObjectId
from flask import Blueprint, send_file
from firefly.db import get_db


# pylint: disable=invalid-name
bp = Blueprint("archive", __name__, url_prefix="/archive")


def save_file(url, link_id):
    session = HTMLSession()
    response = session.get(url)

    content_type = response.headers["content-type"].split(";")[0]
    extension = mimetypes.guess_extension(content_type)
    if extension is None:
        extension = ".html"

    filename = f"{link_id}{extension}"

    fs = gridfs.GridFS(get_db("archive"))
    return fs.put(response.content, filename=filename)


@bp.route("/view/<id>/")
def archive_detail(id):
    fs = gridfs.GridFS(get_db("archive"))

    try:
        doc = fs.get(ObjectId(id))
    except gridfs.errors.NoFile:
        return "No such file found", 404

    return send_file(doc, attachment_filename=doc.filename)
