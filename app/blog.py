from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from app.db import get_db

from markdown import Markdown

import click
from flask.cli import with_appcontext


bp = Blueprint("blog", __name__)

@bp.route("/", methods=("GET",))
def index():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, name"
        " FROM post p JOIN author a ON p.author_id = a.id"
        " ORDER BY created DESC"
    )

    legacy = db.execute(
        "SELECT id, title, body"
        " FROM legacy_post"
        " ORDER BY id DESC"
    ).fetchall()

    first = posts.fetchone()
    rest = posts.fetchall()
    content = None

    if first is not None:
        content = Markdown().convert(first["body"])

    return render_template("blog/index.html", content=content, first=first, rest=rest, legacy=legacy)
