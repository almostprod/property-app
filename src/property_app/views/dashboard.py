from property_app.lib.inertia import InertiaRequest, InertiaHTTPEndpoint


class Dashboard(InertiaHTTPEndpoint):
    def get(self, request: InertiaRequest):
        content = request.query_params.get("content")
        return {"pageContent": content}
