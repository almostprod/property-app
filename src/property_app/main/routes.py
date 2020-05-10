import os
import json
import pathlib

from starlette.requests import Request
from starlette.responses import RedirectResponse

from .router import main
from .views.index import Index
from .views.user import UserList, UserDetail

_LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))

main.add_route("/", Index)
main.add_route("/users", UserList)
main.add_route("/users/{id:int}", UserDetail)


@main.route("/pages/{page_path:path}")
def page_assets(request: Request):
    page_path = request.path_params["page_path"]

    manifest = None
    app_dir = pathlib.Path(_LOCAL_DIR).parent
    manifest_path = app_dir / pathlib.Path("static/dist/manifest.json")
    with open(manifest_path, "rb") as manifest_file:
        manifest = json.load(manifest_file)

    dist_dir = pathlib.Path("dist")
    asset_name = pathlib.Path(manifest[page_path])

    asset_path = dist_dir / asset_name

    asset_url = request.url_for("static", path=asset_path.as_posix())

    return RedirectResponse(asset_url)


@main.route("/favicon.ico")
def favicon(request: Request):
    asset_url = request.url_for("static", path="home-solid.svg")
    return RedirectResponse(asset_url)


"""
1. refer to react pages instead of to jinja template
2. each blueprint has its own package.json etc
3. one blueprint can depend on another. make this explicit?
4. use yarn workspaces to handle deps across blueprints
5. per blueprint rollup config? project wide?
6. integrate with assets and url_for? s3? cdn?
7. need client side url resolving helper
8. integrate with inertia.js for the protocol.

9. show bundle size on build like next.js
10. use dataclasses or WTForms to specify page props?
11. could generate proptype or jsonschema
    from python classes to help with alignment?
12. interop between flask-assets and rollup
13. "render" from view handles the logic of if it will return
    html or json and add headers etc.
14. Some sort of integration with formik?
"""
