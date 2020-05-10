from . import InertiaRequest, InertiaHTTPEndpoint


class UserList(InertiaHTTPEndpoint):
    def get(self, request: InertiaRequest):
        users = [{"id": 1, "name": "Anthony"}, {"id": 2, "name": "Nolan"}]
        return {"users": users}
