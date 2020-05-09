import os

from starlette.applications import Starlette
from starlette.routing import Router
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

local_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(local_dir, "templates"))

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
