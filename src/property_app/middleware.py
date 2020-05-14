import time

from contextvars import ContextVar

from sqlalchemy_mixins.session import NoSessionError  # type: ignore
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette_authlib.middleware import AuthlibMiddleware as SessionMiddleware

from starlette.authentication import (
    AuthenticationBackend,
    UnauthenticatedUser,
    AuthCredentials,
)

from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware  # type: ignore

from sqlalchemy_mixins.activerecord import ModelNotFoundError


class PasswordAuthBackend(AuthenticationBackend):
    def get_user(self, request):
        from property_app.models import auth

        user_email = request.session.get("email")
        if user_email:
            try:
                user_email = auth.AppUserEmail.where(email=user_email).first()
                if user_email:
                    return user_email.user
            except ModelNotFoundError:
                request.session.clear()

    async def authenticate(self, request):
        user = self.get_user(request)

        if user and user.is_authenticated:
            scopes = ["authenticated"] + sorted([str(s) for s in user.scopes])
            return AuthCredentials(scopes), user

        scopes = ["unauthenticated"]
        return AuthCredentials(scopes), UnauthenticatedUser()


class CanonicalLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        from property_app.logging import get_logger

        log = get_logger("property_app")

        request_start = time.perf_counter()

        log.info("request start")

        response = await call_next(request)

        request_time = time.perf_counter() - request_start
        log.info(f"request end {request_time}")

        return response


class DatabaseSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        from property_app.database.session import Session
        from property_app.database import AppBase

        try:
            request_session = AppBase.session  # noqa
        except NoSessionError:
            request_session = Session()
            AppBase.set_session(request_session)

        response = await call_next(request)

        Session.remove()

        return response


class RequestMetaMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        import uuid

        request_id = str(uuid.uuid4())

        _request_id_ctx_var.set(request_id)
        request.state.request_id = request_id

        return await call_next(request)


def get_middleware(config=None):
    """
    Setup app middleware

    """
    from property_app.config import get_config

    if config is None:
        config = get_config()

    return [
        Middleware(ProxyHeadersMiddleware),
        Middleware(
            SessionMiddleware,
            secret_key=str(config.SECRET_KEY),
            session_cookie="_session",
            https_only=True,
            domain=config.DOMAIN,
        ),
        Middleware(RequestMetaMiddleware),
        Middleware(DatabaseSessionMiddleware),
        Middleware(AuthenticationMiddleware, backend=PasswordAuthBackend()),
        Middleware(CanonicalLogMiddleware),
    ]


_request_id_ctx_var: ContextVar[str] = ContextVar(
    "request_id", default=None  # type: ignore
)


def get_request_id() -> str:
    return _request_id_ctx_var.get()
