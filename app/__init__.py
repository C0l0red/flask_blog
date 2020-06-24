from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from jinja2_pluralize import pluralize_dj
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.sqlite3'
    app.config["SECRET_KEY"] = 'dev'

    db.init_app(app)
    ma.init_app(app)
    login_manager.init_app(app)

    migrate = Migrate(app, db)
    from .commands import create_tables, drop_tables, database, populate
    app.cli.add_command(create_tables)
    app.cli.add_command(drop_tables)
    app.cli.add_command(database)
    app.cli.add_command(populate)

    from .auth.routes import auth
    from .post.routes import post
    app.register_blueprint(auth)
    app.register_blueprint(post)

    @app.template_filter("pluralize")
    def pluralize(value, args='s'):
        return pluralize_dj(value, args)

    return app
