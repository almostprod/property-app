from . import InertiaRequest, InertiaHTTPEndpoint

_USERS = [{"id": 1, "name": "Anthony"}, {"id": 2, "name": "Nolan"}]
_USERS_INDEX = {user["id"]: user for user in _USERS}


class UserList(InertiaHTTPEndpoint):
    def get(self, request: InertiaRequest):
        return {"users": _USERS}


class UserDetail(InertiaHTTPEndpoint):
    def get(self, request: InertiaRequest):
        user_id = request.path_params["id"]

        return {"user": _USERS_INDEX.get(user_id)}
