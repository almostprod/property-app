from starlette.authentication import requires

from property_app.lib.inertia import InertiaRequest, InertiaHTTPEndpoint


class Dashboard(InertiaHTTPEndpoint):
    @requires(["authenticated"], redirect="Index")
    def get(self, request: InertiaRequest):
        return {"userProfile": {"username": request.user.username}}
