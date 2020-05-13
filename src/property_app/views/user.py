from property_app.lib.inertia import InertiaRequest, InertiaHTTPEndpoint

_USERS = [{"id": 1, "name": "Anthony"}, {"id": 2, "name": "Nolan"}]
_USERS_INDEX = {user["id"]: user for user in _USERS}


class UserList(InertiaHTTPEndpoint):
    def get(self, request: InertiaRequest):
        return {
            "users": _USERS,
            "indexUrl": request.url_for("Index"),
            "signUpUrl": request.url_for("SignUp"),
            "signOutUrl": request.url_for("SignOut"),
            "dashboardUrl": request.url_for("Dashboard"),
            "usersUrl": request.url_for("UserList"),
        }


class UserDetail(InertiaHTTPEndpoint):
    def get(self, request: InertiaRequest):
        user_id = request.path_params["id"]

        return {
            "user": _USERS_INDEX.get(user_id),
            "indexUrl": request.url_for("Index"),
            "signUpUrl": request.url_for("SignUp"),
            "signOutUrl": request.url_for("SignOut"),
            "dashboardUrl": request.url_for("Dashboard"),
            "usersUrl": request.url_for("UserList"),
        }
