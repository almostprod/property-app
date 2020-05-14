import os

from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles

from property_app.logging import get_logger
from property_app.lib.jinja import get_templates

log = get_logger("property_app")


def create_app(app_config=None):
    from property_app.config import get_config
    from property_app import middleware, logging
    from property_app import routes

    if app_config is None:
        app_config = get_config()

    logging.initialize_logging(log_mode=app_config.LOG_MODE)

    starlette_app = Starlette(
        debug=app_config.DEBUG, middleware=middleware.get_middleware(app_config)
    )

    local_dir = os.path.dirname(os.path.abspath(__file__))

    starlette_app.mount(
        "/static",
        app=StaticFiles(directory=os.path.join(local_dir, "static")),
        name="static",
    )

    starlette_app.mount(
        "/assets", app=StaticFiles(directory="dist/assets/"), name="assets",
    )

    routes.init_app(starlette_app)

    return starlette_app


def start(reload=None):
    import uvicorn  # type: ignore
    from property_app.config import get_config

    config = get_config()

    if config.DEBUG:
        start_app = "property_app.app:app"
    else:
        start_app = create_app(app_config=config)

    if reload is None:
        reload = config.DEBUG

    uvicorn.run(
        start_app,
        host=config.APP_HOST,
        port=config.APP_PORT,
        log_level="info",
        reload=reload,
    )


templates = get_templates()
app = create_app()
