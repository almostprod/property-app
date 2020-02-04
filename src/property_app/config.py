from __future__ import annotations

import os
from distutils.util import strtobool

import structlog
from flask import Flask


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
    # import warnings
    #
    # warnings.filterwarnings("ignore", category=SomeWarning)
    pass


def init_app(app: Flask, app_config: Config = None):
    _suppress_warnings()

    if app_config is None:
        app_config = _config_by_environment(app.env)

    app.config.from_object(app_config)
    if not structlog.is_configured():
        from property_app.logging import initialize_logging

        initialize_logging()

    app_config.init_app(app)


class Config:
    DEBUG = False
    TESTING = False
    PREFERRED_URL_SCHEME = "https"

    SECRET_KEY = env_str("SECRET_KEY", "iqahRzJWhRdnonK9TybtvzTL")
    ENABLE_DEBUG_TOOLBAR = env_bool("DEBUG_TOOLBAR", False)
    TOOLBAR_EXCLUDE_ROUTES =["/slack"]
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_TRACK_MODIFICATIONS = env_bool("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    SQLALCHEMY_DATABASE_URI = env_str("DATABASE_URI")
    SQLALCHEMY_BATCH_MODE = env_bool("DATABASE_BATCH_MODE", True)

    REDIS_URL = env_str("REDIS_URL", "redis://redis:6379/0")
    RQ_REDIS_URL = env_str("RQ_REDIS_URL", REDIS_URL)
    RQ_DASHBOARD_REDIS_URL = env_str("RQ_REDIS_URL", "redis://redis:6379/0")
    RQ_DASHBOARD_POLL_INTERVAL = 2500
    RQ_QUEUES = ["high", "normal", "low"]
    RQ_SCHEDULER_QUEUE = ["scheduled"]

    APP_LOG_LEVEL = env_str("APP_LOG_LEVEL", "DEBUG")


class ProductionConfig(Config):

    @staticmethod
    def init_app(app: Flask):
        import logging

        app_logger = logging.getLogger(app.name)

        for handler in app_logger.handlers[:]:
            handler.setLevel(app.config["APP_LOG_LEVEL"])


class DevelopmentConfig(Config):
    DEBUG = True

    @staticmethod
    def init_app(app: Flask):
        import logging

        app_logger = logging.getLogger(app.name)

        for handler in app_logger.handlers[:]:
            handler.setLevel(app.config["APP_LOG_LEVEL"])


class TestingConfig(Config):
    TESTING = True

    @staticmethod
    def init_app(app: Flask):
        import logging

        app_logger = logging.getLogger(app.name)

        for handler in app_logger.handlers[:]:
            handler.setLevel(app.config["APP_LOG_LEVEL"])
