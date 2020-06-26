from flask.cli import with_appcontext
import click
from flask_migrate import MigrateCommand
from . import db
from .models import User, Comment, BlogPost

@click.command(name="create_tables")
@with_appcontext
def create_tables():
    db.create_all()

@click.command(name="drop_tables")
@with_appcontext
def drop_tables():
    db.drop_all()

@click.command(name="db")
def database():
    MigrateCommand

@click.command(name="populate")
@with_appcontext
def populate():
    red = User(username="Red", email="blaizepaschal@gmail.com")
    polly = User(username="Polly", email="pollyweaver@gmail.com")
    pink = User(username="Pink", email="pink@gmail.com")
    red.set_password("password")
    polly.set_password("password")
    pink.set_password("password")
    post1 = BlogPost(title="post 1", content="content 1 and stuff", author=red)
    post2 = BlogPost(title="post 2", content="content 2", author=pink)
    post3 = BlogPost(title="post 3", content="content 3 .........", author=polly)
    db.session.add(red)
    db.session.add(polly)
    db.session.add(pink)
    post1.like(polly)
    post1.like(red)
    post1.dislike(pink)
    db.session.commit()