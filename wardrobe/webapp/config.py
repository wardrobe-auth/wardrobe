import os

APP_DIR = os.path.dirname(__file__)
BASE_POSTCSS_BIN = os.path.join(
    os.path.dirname(os.path.dirname(APP_DIR)), "node_modules/postcss-cli/bin/postcss"
)

DEFAULT_SECRET_KEY = "Uphooh4CheiQuoosez8Shieb9aesu1taeHa6cheiThuud2taijoh0kei2ush2sie"

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_USER = os.environ.get("DB_USER", "wardrobe")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "secret11!")
DB_DATABASE = os.environ.get("DB_DATABASE", "wardrobe")
DB_ENGINE = os.environ.get("DB_ENGINE", "postgres")
DB_SCHEME = "postgresql+psycopg2"

if DB_ENGINE == "mysql":
    DB_SCHEME = "mysql+mysqlconnector"

SQLALCHEMY_DATABASE_URI = (
    f"{DB_SCHEME}://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/"
    f"{DB_DATABASE}"
)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or DEFAULT_SECRET_KEY

    ASSETS_DEBUG = os.environ.get("ASSETS_DEBUG", "False") == "True"
    POSTCSS_BIN = os.environ.get("POSTCSS_BIN", BASE_POSTCSS_BIN)

    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OAUTH2_REFRESH_TOKEN_GENERATOR = True
    OAUTH2_JWT_SECRET_KEY = os.environ.get("OAUTH2_JWT_SECRET_KEY", "secret-key")
    OAUTH2_JWT_ALG = os.environ.get("OAUTH2_JWT_ALG", "RS512")
    OAUTH2_JWT_ISS = os.environ.get("OAUTH2_JWT_ISS", "https://wardrobe-auth.github.io/wardrobe")
    OAUTH2_JWT_EXP = int(os.environ.get("OAUTH2_JWT_EXP", 3600))

    # Flask-Mail SMTP server settings
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = os.environ.get("MAIL_PORT", 465)
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "True") == "True"
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "False") == "True"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")

    # Flask-User settings
    USER_APP_NAME = os.environ.get("USER_APP_NAME")
    USER_ENABLE_EMAIL = True  # Enable email authentication
    USER_ENABLE_USERNAME = False  # Disable username authentication
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = os.environ.get("USER_EMAIL_SENDER_EMAIL")
    # USER_ENABLE_REGISTER = True

    SOCIAL_AUTO_REGISTER_USER = True
    SOCIAL_URL_PREFIX = "/social"
    SOCIAL_USE_HTTPS = os.environ.get("SOCIAL_USE_HTTPS", "False") == "True"
    SOCIAL_FACEBOOK = {
        "consumer_key": os.environ.get("FACEBOOK_CLIENT_ID", "facebook app id"),
        "consumer_secret": os.environ.get(
            "FACEBOOK_CLIENT_SECRET", "facebook app secret"
        ),
    }

    SOCIAL_GOOGLE = {
        "consumer_key": os.environ.get("GOOGLE_CLIENT_ID", "google app id"),
        "consumer_secret": os.environ.get("GOOGLE_CLIENT_SECRET", "google app secret"),
    }

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class DockerConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler

        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler

        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.INFO)
        app.logger.addHandler(syslog_handler)


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "docker": DockerConfig,
    "unix": UnixConfig,
    "default": DevelopmentConfig,
}
