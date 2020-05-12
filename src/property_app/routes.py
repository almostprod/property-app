import json
import pathlib

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Router
from starlette.responses import RedirectResponse

from .views.index import Index
from .views.dashboard import Dashboard
from .views.signup import SignUp
from .views.user import UserList, UserDetail

routes = Router()


def init_app(app: Starlette, path="/", name=None):
    app.mount(path, routes, name=name)
    return app


routes.add_route("/", Index)
routes.add_route("/signup", SignUp)
routes.add_route("/dashboard", Dashboard)
routes.add_route("/users", UserList)
routes.add_route("/users/{id:int}", UserDetail)


@routes.route("/pages/{page_path:path}")
def page_assets(request: Request):
    from property_app.config import get_config

    config = get_config()
    dist_root = config.DIST_ROOT

    page_path = request.path_params["page_path"]

    manifest = None
    dist_dir = pathlib.Path(dist_root)
    manifest_path = dist_dir / pathlib.Path("assets/manifest.json")
    with open(manifest_path, "rb") as manifest_file:
        manifest = json.load(manifest_file)

    asset_name = pathlib.Path(manifest[page_path])
    asset_url = request.url_for("assets", path=asset_name.as_posix())

    return RedirectResponse(asset_url)


@routes.route("/favicon.ico")
def favicon(request: Request):
    asset_url = request.url_for("static", path="home-solid.svg")
    return RedirectResponse(asset_url)
