from __future__ import annotations

import os
import typing
from distutils.util import strtobool

import structlog
from starlette.config import Config
from starlette.datastructures import URL, Secret

config = Config(".env")


def env_bool(envar, default=False) -> bool:
    return strtobool(os.environ.get(envar, str(default)))


def env_int(envar, default=0) -> int:
    return int(os.environ.get(envar, int(default)))


def env_str(envar, default="") -> str:
    return os.environ.get(envar, str(default))


def _config_by_environment(app_environment: str):
    environments = dict(
        development=DevelopmentConfig,
        testing=TestingConfig,
        production=ProductionConfig,
    )

    return environments.get(app_environment, DevelopmentConfig)


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
    ASGI_APP = config("ASGI_APP", default="app")
    APP_BUILD_HASH = env_str("APP_BUILD_HASH", default="dev")

    DEBUG = config("DEBUG", cast=bool, default=False)
    TESTING = config("TESTING", cast=bool, default=False)

    SECRET_KEY = config("SECRET_KEY", cast=Secret, default="asecretkey")

    DATABASE_URI = config("DATABASE_URI", cast=URL)

    REDIS_URL = config("REDIS_URL", cast=URL, default="redis://redis:6379/0")

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


def get_config(app_env: typing.Optional[str] = None) -> Config:

    if app_env is None:
        app_env = config("APP_ENV")

    return _config_by_environment(app_env)
