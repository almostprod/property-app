from property_app.lib.inertia import InertiaRequest, InertiaHTTPEndpoint


class Dashboard(InertiaHTTPEndpoint):
    def get(self, request: InertiaRequest):
        return {"userProfile": {"username": request.user.username}}
