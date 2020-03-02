from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import UJSONResponse
from starlette.routing import Route
from property_app.models.auth import AppUser


def index(request: Request):
    name = request.query_params.get("username")
    if name is not None:
        AppUser.create(username=name)
        AppUser.session.commit()

    users = AppUser.all()

    return UJSONResponse({"users": [u.to_dict() for u in users]})


routes = [Route("/", index)]


def create_app(app_config=None):
    from property_app.config import get_config
    from property_app import middleware

    # TODO: Logging, Database

    if app_config is None:
        app_config = get_config()

    starlette_app = Starlette(debug=app_config.DEBUG, routes=routes,)

    middleware.init_app(starlette_app)

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


app = create_app()
