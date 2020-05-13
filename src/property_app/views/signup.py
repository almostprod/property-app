from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError, validator
from pydantic import EmailStr, SecretStr

from starlette.responses import RedirectResponse

from property_app.lib.inertia import InertiaRequest, InertiaHTTPEndpoint


class SignUpForm(BaseModel):
    email: EmailStr
    password: SecretStr
    password_confirm: SecretStr = Field(alias="passwordConfirm")

    @validator("password_confirm")
    def passwords_match(cls, value, values):

        if values["password"] != value:
            raise ValueError("Password confirmation failed")

        return value


class SignUp(InertiaHTTPEndpoint):
    def get(self, request: InertiaRequest):

        if request.user.is_authenticated:
            return RedirectResponse(
                request.url_for("Dashboard"),
                headers={"X-Inertia": "true"},
                status_code=303,
            )

        return {}

    def post(self, request: InertiaRequest, json_body: dict):

        try:
            signup_form = SignUpForm.parse_obj(json_body)
            request.session["auth_token"] = signup_form.email
        except ValidationError as e:
            return {"errors": e.errors()}

        return RedirectResponse(
            request.url_for("Dashboard"), headers={"X-Inertia": "true"}, status_code=303
        )
