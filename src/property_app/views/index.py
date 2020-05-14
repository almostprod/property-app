from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError
from pydantic import EmailStr, SecretStr

from passlib.apps import custom_app_context

from starlette.authentication import requires
from property_app.lib.inertia import InertiaRequest, InertiaHTTPEndpoint

from property_app.models import auth


class LoginForm(BaseModel):
    email: EmailStr
    password: SecretStr
    remember_me: bool = Field(alias="rememberMe")


class Index(InertiaHTTPEndpoint):
    @requires(["unauthenticated"], redirect="Dashboard")
    def get(self, request: InertiaRequest):
        return {
            "indexUrl": request.url_for("Index"),
            "signUpUrl": request.url_for("SignUp"),
            "dashboardUrl": request.url_for("Dashboard"),
            "usersUrl": request.url_for("UserList"),
        }

    def post(self, request: InertiaRequest, json_body: dict):

        try:
            login_form = LoginForm.parse_obj(json_body)

            user_email = auth.AppUserEmail.where(email=login_form.email).first()
            if user_email:
                user = user_email.user

                for credential in user.credentials:
                    is_valid = custom_app_context.verify(
                        login_form.password.get_secret_value(), credential.credential
                    )

                    if is_valid:
                        request.session.update(
                            {"iss": "app", "email": user.email, "scopes": user.scopes}
                        )
                        break

        except ValidationError as e:
            return {"errors": e.errors()}

        return request.redirect(request.url_for("Dashboard"))
