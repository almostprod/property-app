import os
import pathlib
import json

import jinja2

from starlette.applications import Starlette
from starlette.routing import Router
from starlette.templating import Jinja2Templates

_LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))


@jinja2.contextfunction
def asset_url(context: dict, name: str, dist_root=None):
    if dist_root is None:
        from property_app.config import get_config

        config = get_config()
        dist_root = config.DIST_ROOT

    manifest = None
    dist_path = pathlib.Path(dist_root)
    manifest_path = dist_path / pathlib.Path("assets/manifest.json")
    with open(manifest_path, "rb") as manifest_file:
        manifest = json.load(manifest_file)

    asset_name = pathlib.Path(manifest[name])

    request = context["request"]

    return request.url_for("assets", path=asset_name.as_posix())


templates = Jinja2Templates(directory=os.path.join(_LOCAL_DIR, "templates"))

jinja_env = templates.env
jinja_env.globals["asset_url"] = asset_url


main = Router()


def init_app(app: Starlette, path="/", name=None):
    from . import routes  # noqa

    app.mount(path, main, name=name)
    return app
