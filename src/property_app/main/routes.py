from starlette.requests import Request
from starlette.responses import UJSONResponse
from property_app.models.auth import AppUser

from .router import main


@main.route("/", ["GET"], name="index")
def index(request: Request):
    name = request.query_params.get("username")

    if name is not None:
        AppUser.create(username=name)
        AppUser.session.commit()

    users = AppUser.all()

    return UJSONResponse({"users": [u.to_dict() for u in users]})


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
11. could generate proptype or jsonschema from python classes to help with alignment?
12. interop between flask-assets and rollup
13. "render" from view handles the logic of if it will return html or json and add headers etc.
14. Some sort of integration with formik?
"""
