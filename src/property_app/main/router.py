import os
import pathlib
import json

import jinja2

from starlette.applications import Starlette
from starlette.routing import Router
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates


@jinja2.contextfunction
def asset_url(context: dict, name: str):
    manifest = None
    app_dir = pathlib.Path(local_dir).parent
    manifest_path = app_dir / pathlib.Path("static/dist/manifest.json")
    with open(manifest_path, "rb") as manifest_file:
        manifest = json.load(manifest_file)

    dist_dir = pathlib.Path("dist")
    asset_name = pathlib.Path(manifest[name])

    asset_path = dist_dir / asset_name

    request = context["request"]

    return request.url_for("static", path=asset_path.as_posix())


local_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(local_dir, "templates"))

jinja_env = templates.env
jinja_env.globals["asset_url"] = asset_url


main = Router()

main.mount(
    "/main/public",
    app=StaticFiles(directory=os.path.join(local_dir, "public")),
    name="main:public",
)


def init_app(app: Starlette, path="/", name=None):
    from . import routes  # noqa

    app.mount(path, main, name=name)
    return app
