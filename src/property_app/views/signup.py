from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError, validator
from pydantic import EmailStr, SecretStr

from passlib.apps import custom_app_context

from property_app.lib.inertia import InertiaRequest, InertiaHTTPEndpoint

from property_app.models import auth


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
            return request.redirect(request.url_for("Dashboard"),)

        return {}

    def post(self, request: InertiaRequest, json_body: dict):

        try:
            signup_form = SignUpForm.parse_obj(json_body)

            user_email = auth.AppUserEmail.where(email=signup_form.email).first()
            if not user_email:

                password = auth.AppUserCredential(
                    credential=custom_app_context.hash(str(signup_form.password))
                )

                user = auth.AppUser.create(
                    scopes=["self:read", "self:write"],
                    emails=[auth.AppUserEmail(email=signup_form.email)],
                    credentials=[password],
                )
                user.save()

                request.session.update(
                    {"iss": "app", "email": user.email, "scopes": user.scopes}
                )

                user.session.commit()

        except ValidationError as e:
            return {"errors": e.errors()}

        return request.redirect(request.url_for("Dashboard"))


class SignOut(InertiaHTTPEndpoint):
    def post(self, request: InertiaRequest, json_body: dict):

        if request.session:
            request.session.clear()

        return request.redirect(request.url_for("Index"))
