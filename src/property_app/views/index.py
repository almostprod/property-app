from starlette.authentication import requires
from property_app.lib.inertia import InertiaRequest, InertiaHTTPEndpoint


class Index(InertiaHTTPEndpoint):
    @requires(["unauthenticated"], redirect="Dashboard")
    def get(self, request: InertiaRequest):
        return {
            "indexUrl": request.url_for("Index"),
            "signUpUrl": request.url_for("SignUp"),
            "dashboardUrl": request.url_for("Dashboard"),
            "usersUrl": request.url_for("UserList"),
        }
