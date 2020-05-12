from property_app.lib.inertia import InertiaRequest, InertiaHTTPEndpoint


class SignUp(InertiaHTTPEndpoint):
    def get(self, request: InertiaRequest):
        return {}
