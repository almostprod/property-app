from . import InertiaRequest, InertiaHTTPEndpoint


class Index(InertiaHTTPEndpoint):
    def get(self, request: InertiaRequest):
        content = request.query_params.get("content")
        return {"pageContent": content}
