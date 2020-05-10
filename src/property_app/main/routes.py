from starlette.requests import Request

from .router import main, templates
from ..logging import get_logger

log = get_logger("property_app")


@main.route("/", ["GET"], name="index")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


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
