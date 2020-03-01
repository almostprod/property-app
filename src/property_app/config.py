from __future__ import annotations

import os
from distutils.util import strtobool

import structlog
from starlette.config import Config
from starlette.datastructures import URL, Secret

config = Config(".env")

# DEBUG = config('DEBUG', cast=bool, default=False)
# TESTING = config('TESTING', cast=bool, default=False)
# SECRET_KEY = config('SECRET_KEY', cast=Secret)
#
# DATABASE_URL = config('DATABASE_URL', cast=URL)
# if TESTING:
#     DATABASE_URL = DATABASE_URL.replace(database='test_' + DATABASE_URL.database)


def env_bool(envar, default=False) -> bool:
    return strtobool(os.environ.get(envar, str(default)))


def env_int(envar, default=0) -> int:
    return int(os.environ.get(envar, int(default)))


def env_str(envar, default="") -> str:
    return os.environ.get(envar, str(default))


def _config_by_environment(flask_environment: str):
    environments = dict(development=DevelopmentConfig, testing=TestingConfig, production=ProductionConfig)

    return environments.get(flask_environment, DevelopmentConfig)


def _suppress_warnings():
    # warnings.filterwarnings("ignore", category=SomeWarning)
    pass


def init_app(app, app_config: Config = None):
    _suppress_warnings()

    if app_config is None:
        app_config = _config_by_environment(app.env)

    app.config.from_object(app_config)
    if not structlog.is_configured():
        from property_app.logging import initialize_logging

        initialize_logging()

    app_config.init_app(app)


class Config:
    DEBUG = config('DEBUG', cast=bool, default=False)
    TESTING = config('TESTING', cast=bool, default=False)

    SECRET_KEY = config("SECRET_KEY", cast=Secret, default="asecretkey")

    SQLALCHEMY_DATABASE_URI = config("DATABASE_URI")

    REDIS_URL = config("REDIS_URL", default="redis://redis:6379/0")

    APP_LOG_LEVEL = config("APP_LOG_LEVEL", default="DEBUG")


class ProductionConfig(Config):

    @staticmethod
    def init_app(app):
        import logging

        app_logger = logging.getLogger(app.name)

        for handler in app_logger.handlers[:]:
            handler.setLevel(app.config["APP_LOG_LEVEL"])


class DevelopmentConfig(Config):
    DEBUG = True

    @staticmethod
    def init_app(app):
        import logging

        app_logger = logging.getLogger(app.name)

        for handler in app_logger.handlers[:]:
            handler.setLevel(app.config["APP_LOG_LEVEL"])


class TestingConfig(Config):
    TESTING = True

    @staticmethod
    def init_app(app):
        import logging

        app_logger = logging.getLogger(app.name)

        for handler in app_logger.handlers[:]:
            handler.setLevel(app.config["APP_LOG_LEVEL"])
