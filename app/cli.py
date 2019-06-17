import os
from sys import platform

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from app.db import get_db

import click
from flask.cli import with_appcontext

bp = Blueprint("cli", __name__)

TEMP_FILE_NAME = "~temporary_file~.txt"

def open_in_editor(filename):
    if platform == "linux" or platform == "linux2":
        os.system(f"{os.getenv('EDITOR')} {filename}")
    elif platform == "win32":
        os.system(f"{filename}")
    else:
        f"platform {platform} not supported."

@click.command("add-post")
@click.argument("title")
@click.option("--legacy", default=False)
@click.option("--filename", default=TEMP_FILE_NAME)
@click.option("--author", default=None, help="Name of author")
@with_appcontext
def add_post_command(title, legacy, filename, author):
    """Add a legacy-style post to the website with a title, and contents from a file."""
    
    if not legacy and author is None:
        print("Please give the id of an author.")
        return
    elif legacy and author is not None:
        print("Legacy posts dont have authors.")
        return

    db = get_db()
    file_is_temp = False

    if not os.path.isfile(filename):
        open(filename, "w+").close()
        open_in_editor(filename)
        file_is_temp = True

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
    
    if file_is_temp:
        os.remove(filename)

@click.command("add-author")
@click.argument("name")
@click.option("--picture", default=None, help="Url of picture, relative to static/")
@click.option("--description", default="", help="Description of the author")
@with_appcontext
def add_author_command(name, picture, description):
    db = get_db()
    db.execute(
        "INSERT INTO author (name, picture_url, description)"
        " VALUES (?, ?, ?)",
        (name, picture, description)
    )

    db.commit()

@click.command("edit-post")
@click.argument("id")
@click.option("--new-title", default=None)
@click.option("--legacy", default=False)
@click.option("--filename", default=TEMP_FILE_NAME)
@with_appcontext
def edit_post_command(id, new_title, legacy, filename):
    db = get_db()
    post = None
    if not legacy:
        post = db.execute(
            "SELECT title, body"
            " FROM post"
            " WHERE id = ?",
            (id,)
        ).fetchone()
    else: 
        post = db.execute(
            "SELECT title, body FROM legacy_post WHERE id = ?",
            (id,)
        ).fetchone()
    
    if post is None:
        print(f"Post with id {id} not found.")
        return
    
    with open(filename, "w+") as f:
        f.write(post["body"])
    
    open_in_editor(filename)

    title = new_title if new_title is not None else post["title"]

    with open(filename, "r+") as f:
        if not legacy:
            db.execute(
                "UPDATE post"
                " SET title = ?, body = ?"
                " WHERE id = ?",
                (title, f.read(), id)
            )
        else:
            db.execute(
                "UPDATE legacy_post"
                " SET title = ?, body = ?"
                " WHERE id = ?",
                (title, f.read(), id)
            )
    db.commit()
    os.remove(filename)

    

def init_app(app):
    app.cli.add_command(add_post_command)
    app.cli.add_command(add_author_command)
    app.cli.add_command(edit_post_command)
