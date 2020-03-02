from starlette.applications import Starlette
from starlette.routing import Router

main = Router()


def init_app(app: Starlette, path="/", name=None):
    from . import routes  # noqa

    app.mount(path, main, name=name)
    return app
