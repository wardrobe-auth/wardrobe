import logging.config
from datetime import datetime

from flask import Flask
from webassets import Bundle

from flask_social_login import SQLAlchemyConnectionDatastore
from wardrobe.repositories.sqla.models import User, Connection, Role
from wardrobe.rest.config import config
from wardrobe.rest.database import db, migrate
from wardrobe.rest.extensions import assets, cors, ma
from wardrobe.rest.social import social
from wardrobe.rest.user import user_manager
from wardrobe.services.oauth2 import config_oauth


def create_app(config_name="default", settings_override=None):
    app = Flask(__name__)
    app_config = config[config_name]
    app.config.from_object(app_config)
    app_config.init_app(app)

    init_db(app)

    user_manager.init_app(app, db, User)
    app.extensions["login_manager"] = user_manager.login_manager

    init_assets(app)
    init_extensions(app)
    init_social(app, db)

    if settings_override:
        app.config.update(settings_override)

    init_blueprint(app)
    init_commands(app)
    config_oauth(app)

    return app


def init_assets(app):
    assets.init_app(app)
    css_all = Bundle("src/css/*.css", filters="postcss", output="dist/css/main.css")

    assets.register("css_all", css_all)


def init_logging():
    LOGGING = {
        "version": 1,
        "formatters": {
            "brief": {"format": "%(message)s"},
            "default": {
                "format": "%(asctime)s %(levelname)-8s %(name)-15s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "none": {"class": "logging.NullHandler"},
        },
        "loggers": {
            "amqp": {"handlers": ["none"], "propagate": False},
            "conf": {"handlers": ["none"], "propagate": False},
            "": {
                "handlers": [
                    "console",
                ],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(LOGGING)


def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)


def init_extensions(app):
    cors.init_app(
        app,
        resources={
            r"/*": {"origins": "*"},
        },
    )
    ma.init_app(app)


def init_social(app, db):
    def wrapper(db, User, Connection):
        def connection_not_found_handler(cv):
            user = User()
            user.active = True
            if cv["email"]:
                user.email = cv["email"]
                user.email_confirmed_at = datetime.utcnow()

            db.session.add(user)
            connection = Connection()
            connection.user = user
            for k, v in cv.items():
                setattr(connection, k, v)

            db.session.add(connection)
            db.session.commit()

            return connection

        return connection_not_found_handler

    app.config["SOCIAL_CONNECTION_NOT_FOUND_HANDLER"] = wrapper(db, User, Connection)

    datastore = SQLAlchemyConnectionDatastore(db, Connection)
    social.init_app(app, datastore)


def init_blueprint(app):
    from wardrobe.rest.api import api as api_bp
    from wardrobe.rest.api import admin as admin_bp
    from wardrobe.rest.oauth import oauth2 as oauth_bp
    from wardrobe.rest.swagger import swagger_bp
    from wardrobe.rest.views import main as main_bp

    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(oauth_bp, url_prefix="/oauth")
    app.register_blueprint(swagger_bp, url_prefix="/swagger")


def init_commands(app):
    @app.cli.command("init-db")
    def init_database():
        db.create_all()

        # Create 'member@example.com' user with no roles
        if (
            not db.session.query(User)
            .filter(User.email == "member@example.com")
            .first()
        ):
            user = User(
                email="member@example.com",
                email_confirmed_at=datetime.utcnow(),
                password=user_manager.hash_password("Password1"),
            )
            db.session.add(user)
            db.session.commit()

        # Create 'admin@example.com' user with 'Admin' and 'Agent' roles
        if not db.session.query(User).filter(User.email == "admin@example.com").first():
            user = User(
                email="admin@example.com",
                email_confirmed_at=datetime.utcnow(),
                password=user_manager.hash_password("Password1"),
            )
            user.roles.append(Role(name="Admin"))
            user.roles.append(Role(name="Agent"))
            db.session.add(user)
            db.session.commit()
