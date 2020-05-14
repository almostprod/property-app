import time

from contextvars import ContextVar

from sqlalchemy_mixins.session import NoSessionError  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
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

        user_id = request.session.get("user")
        if user_id:
            try:
                return auth.AppUser.find_or_fail(user_id)
            except ModelNotFoundError:
                request.session.pop("user")

    async def authenticate(self, request):
        user = self.get_user(request)
        if user and user.is_authenticated:
            scopes = ["authenticated"] + sorted([str(s) for s in user.scopes])
            return AuthCredentials(scopes), user
        scopes = ["unauthenticated"]
        return AuthCredentials(scopes), UnauthenticatedUser()


def init_app(app: Starlette):
    """
    Setup app middleware

    """
    from property_app.database.session import Session
    from property_app.database import AppBase
    from property_app.config import get_config

    config = get_config()

    @app.middleware("http")
    async def canonical_log(request: Request, call_next) -> Response:
        from property_app.logging import get_logger

        log = get_logger("property_app")

        request_start = time.perf_counter()

        log.info("request start")

        response = await call_next(request)

        request_time = time.perf_counter() - request_start
        log.info(f"request end {request_time}")

        return response

    @app.middleware("http")
    async def setup_database_session(request: Request, call_next) -> Response:
        try:
            request_session = AppBase.session  # noqa
        except NoSessionError:
            request_session = Session()
            AppBase.set_session(request_session)

        response = await call_next(request)

        Session.remove()

        return response

    @app.middleware("http")
    async def inject_request_meta(request: Request, call_next) -> Response:
        import uuid

        request_id = str(uuid.uuid4())

        _request_id_ctx_var.set(request_id)
        request.state.request_id = request_id

        return await call_next(request)

    app.add_middleware(ProxyHeadersMiddleware)
    app.add_middleware(AuthenticationMiddleware, backend=PasswordAuthBackend())
    app.add_middleware(
        SessionMiddleware,
        secret_key=config.SECRET_KEY,
        session_cookie="_session",
        https_only=True,
        domain=config.DOMAIN,
    )


_request_id_ctx_var: ContextVar[str] = ContextVar(
    "request_id", default=None  # type: ignore
)


def get_request_id() -> str:
    return _request_id_ctx_var.get()
