def _config_by_environment(cfg, flask_environment):
    environments = dict(
        development=cfg.DevelopmentConfig,
        testing=cfg.TestingConfig,
        production=cfg.ProductionConfig,
    )

    return environments.get(flask_environment, cfg.DevelopmentConfig)


def create_app(app_config=None):
    # from werkzeug.middleware.proxy_fix import ProxyFix

    from . import config

    from .database import AppBase
    from .logging import get_logger

    # @app.before_request
    # def log_request():
    #     from flask import request, current_app
    #
    #     current_app.log.info(
    #         "Request",
    #         blueprint=request.blueprint,
    #         method=request.method,
    #         path=request.path,
    #         body=request.get_data(),
    #     )
    #
    # return app
    pass
