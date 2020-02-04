from __future__ import annotations

import base64
import os
from distutils.util import strtobool
from json import JSONDecodeError
from urllib.parse import quote

import boto3
import structlog
from flask import Flask, json


def env_bool(envar, default=False) -> bool:
    return strtobool(os.environ.get(envar, str(default)))


def env_int(envar, default=0) -> int:
    return int(os.environ.get(envar, int(default)))


def env_str(envar, default="") -> str:
    return os.environ.get(envar, str(default))


def get_secret(secret_name: str, is_binary: bool = False, region: str = "us-east-1", profile=None):

    session = boto3.session.Session(profile_name=profile)
    client = session.client(service_name="secretsmanager", region_name=region)

    secret_values = client.get_secret_value(SecretId=secret_name)

    if is_binary:
        return base64.b64decode(secret_values["SecretString"])

    secret_string = secret_values["SecretString"]

    try:
        return json.loads(secret_string)
    except JSONDecodeError:
        return secret_string


def aws_database_uri(secrets: dict = None):
    if env_str("FLASK_ENV") == "production" or secrets:
        secret_name = env_str("DATABASE_SECRET")
        if not secrets:
            secrets = get_secret(secret_name)

        username = quote(secrets["username"])
        host = secrets["host"]
        port = secrets["port"]
        db_name = quote(secrets["dbname"])
        password = quote(secrets["password"])

        return f"postgresql://{username}:{password}@{host}:{port}/{db_name}?options=-csearch_path=public"

    return None


def _config_by_environment(flask_environment: str):
    environments = dict(development=DevelopmentConfig, testing=TestingConfig, production=ProductionConfig)

    return environments.get(flask_environment, DevelopmentConfig)


def _suppress_warnings():
    import warnings
    from arrow.factory import ArrowParseWarning

    # TODO (amcclosky): Figure out what to upgrade or change to eliminate this warning
    warnings.filterwarnings("ignore", category=ArrowParseWarning)


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
    SQLALCHEMY_DATABASE_URI = aws_database_uri()

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
