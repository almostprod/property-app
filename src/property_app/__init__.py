def _config_by_environment(cfg, flask_environment):
    environments = dict(development=cfg.DevelopmentConfig, testing=cfg.TestingConfig, production=cfg.ProductionConfig)

    return environments.get(flask_environment, cfg.DevelopmentConfig)


def create_app(app_config=None):
    from flask import Flask
    from flask_migrate import Migrate
    from flask_debugtoolbar import DebugToolbarExtension
    from werkzeug.middleware.proxy_fix import ProxyFix

    from . import config
    from . import models  # noqa

    from .database import db
    from .logging import get_logger

    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    config.init_app(app, app_config=app_config)
    db.init_app(app)

    Migrate().init_app(app, db)

    if app.config["ENABLE_DEBUG_TOOLBAR"]:
        toolbar = DebugToolbarExtension()
        toolbar._actual_show_toolbar = toolbar._show_toolbar  # noqa

        def _show_toolbar(self):
            from flask import request
            for route_path in app.config["TOOLBAR_EXCLUDE_ROUTES"]:
                if route_path in request.path:
                    return False

            return self._actual_show_toolbar()

        toolbar._show_toolbar = _show_toolbar.__get__(toolbar, DebugToolbarExtension)

        toolbar.init_app(app)

    from . import main

    app.register_blueprint(main.bp)

    from . import cli

    cli.init_cli(app)

    app.log = get_logger(app.name)

    @app.before_request
    def log_request():
        from flask import request, current_app

        current_app.log.info(
            "Request", blueprint=request.blueprint, method=request.method, path=request.path, body=request.get_data()
        )

    return app
