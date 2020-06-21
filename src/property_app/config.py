from __future__ import annotations

import os
import typing

from starlette.config import Config
from starlette.datastructures import URL, Secret


_LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))


def env_str(envar, default="") -> str:
    return os.environ.get(envar, str(default))


config = Config(env_str("ENV_FILE", default=".env"))


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
    # if not structlog.is_configured():
    #     from property_app.logging import initialize_logging

    #     initialize_logging()


class AppConfig:
    ASGI_APP = config("ASGI_APP", default="app")
    APP_BUILD_HASH = config("APP_BUILD_HASH", default="dev")
    DOMAIN = config("APP_DOMAIN", default="localhost")

    DEBUG = config("DEBUG", cast=bool, default=False)
    TESTING = config("TESTING", cast=bool, default=False)

    SECRET_KEY = config("SECRET_KEY", cast=Secret, default="asecretkey")

    DATABASE_URI = config("DATABASE_URI", cast=URL)

    REDIS_URL = config("REDIS_URL", cast=URL, default="redis://redis:6379/0")

    APP_LOG_LEVEL = config("APP_LOG_LEVEL", default="DEBUG")
    LOG_MODE = config("LOG_MODE", default="local")

    APP_PORT = config("APP_PORT", cast=int, default=5000)
    APP_HOST = config("APP_HOST", cast=str, default="0.0.0.0")

    DIST_ROOT = config("APP_DIST_ROOT", cast=str, default="dist/")
    TEMPLATE_ROOT = config("APP_TEMPLATE_ROOT", cast=str, default=_LOCAL_DIR)

    BASE_DDB_TABLE = config("APP_BASE_DDB_TABLE", cast=str, default="LocalPropertyApp")
    DDB_ENDPOINT = config("APP_DDB_ENDPOINT", cast=URL, default="http://localhost:8000")


class ProductionConfig(AppConfig):

    APP_PORT = config("PORT", cast=int, default=5000)
    DOMAIN = config("RENDER_EXTERNAL_HOSTNAME", default="localhost")

    @staticmethod
    def init_app(app):
        import logging

        app_logger = logging.getLogger(app.name)

        for handler in app_logger.handlers[:]:
            handler.setLevel(app.config["APP_LOG_LEVEL"])


class DevelopmentConfig(AppConfig):
    DEBUG = True

    @staticmethod
    def init_app(app):
        import logging

        app_logger = logging.getLogger(app.name)

        for handler in app_logger.handlers[:]:
            handler.setLevel(app.config["APP_LOG_LEVEL"])


class TestingConfig(AppConfig):
    TESTING = True

    @staticmethod
    def init_app(app):
        import logging

        app_logger = logging.getLogger(app.name)

        for handler in app_logger.handlers[:]:
            handler.setLevel(app.config["APP_LOG_LEVEL"])


def get_config(app_env: typing.Optional[str] = None) -> AppConfig:

    if app_env is None:
        app_env = config("APP_ENV")

    return _config_by_environment(app_env)
