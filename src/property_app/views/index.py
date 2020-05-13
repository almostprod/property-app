from property_app.lib.inertia import InertiaRequest, InertiaHTTPEndpoint


class Index(InertiaHTTPEndpoint):
    def get(self, request: InertiaRequest):
        signup_url = request.url_for("SignUp")
        return {"signUpUrl": signup_url}
