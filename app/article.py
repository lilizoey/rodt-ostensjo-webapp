from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from app.db import get_db

from markdown import Markdown

bp = Blueprint("article", __name__)

@bp.route("/article/<int:id>", methods=("GET",))
def article(id):
    post = get_db().execute(
        "SELECT p.title, p.body, a.id, a.name, a.picture_url"
        " FROM post p JOIN author a ON p.author_id = a.id"
        " WHERE p.id = ?",
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} finnes ikke.")

    content = Markdown().convert(post["body"])

    return render_template("blog/article.html", content=content, post=post)


@bp.route("/legacy/<int:id>", methods=("GET",))
def legacy_article(id):
    post = get_db().execute(
        "SELECT title, body"
        " FROM legacy_post"
        " WHERE id = ?",
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"legacy-post id {id} finnes ikke.")

    content = Markdown().convert(post["body"])

    return render_template("blog/article.html", content=content, post=post)


