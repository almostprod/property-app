from __future__ import annotations

import os
import typing

from starlette.config import Config
from starlette.datastructures import URL, CommaSeparatedStrings


def env_str(envar, default="") -> str:
    return os.environ.get(envar, str(default))


config = Config(env_str("ENV_FILE", default=".env"))


def _config_by_environment(app_environment: str):
    environments = dict(development=DevelopmentConfig, production=ProductionConfig,)

    return environments.get(app_environment, DevelopmentConfig)


def get_config(app_env: typing.Optional[str] = None) -> AppConfig:

    if app_env is None:
        app_env = config("APP_ENV")

    return _config_by_environment(app_env)


class AppConfig:
    DEBUG = config("DEBUG", cast=bool, default=False)
    TESTING = config("TESTING", cast=bool, default=False)

    DATABASE_URI = config("DATABASE_URI", cast=URL)

    APP_LOG_LEVEL = config("APP_LOG_LEVEL", default="DEBUG")
    LOG_MODE = config("LOG_MODE", default="local")

    CSV_EXCLUDE_COLS = config(
        "TCAD_EXCLUDE_COLS", cast=CommaSeparatedStrings, default=["filler"]
    )
    CSV_LOAD_CHUNKSIZE = config("CSV_LOAD_CHUNKSIZE", cast=int, default=1000)


class ProductionConfig(AppConfig):
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
