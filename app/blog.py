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
    ).fetchall()

    first = posts.fetchone()
    rest = posts.fetchall()
    content = None

    if first is not None:
        content = Markdown().convert(first["body"])

    return render_template("blog/index.html", content=content, first=first, rest=rest, legacy=legacy)

@click.command("add-post")
@click.argument("title")
@click.argument("filename")
@click.option("author", default=None, help="Name of author")
@with_appcontext
def add_post_command(title, filename, author):
    """Add a legacy-style post to the website with a title, and contents from a file."""
    
    db = get_db()
    
    if author is None:
        with open(filename) as f:

            db.execute(
                "INSERT INTO legacy_post (title, body)"
                " VALUES (?, ?)",
                (title, f.read())
            )

            db.commit()
        return
    
    author_id = db.execute(
        "SELECT id FROM author WHERE name = ?",
        (author,)
    )

    if author_id is None:
        print("Author not found")
        return
    
    with open(filename) as f:
        db.execute(
            "INSERT INTO post (author_id, title, body)"
            " VALUES (?, ?, ?)",
            (author_id, title, f.read())
        )

@click.command("add-author")
@click.argument("name")
@click.option("picture", default=None, help="Url of picture, relative to static/")
@click.option("description", default="", help="Description of the author")
@with_appcontext
def add_author_command(name, picture, description):
    db = get_db()
    db.execute(
        "INSERT INTO author (name, picture_url, description)"
        " VALUES (?, ?, ?)",
        name, picture, description
    )

    db.commit()

def init_app(app):
    app.cli.add_command(add_post_command)
    app.cli.add_command(add_author_command)
