import time

from contextvars import ContextVar

from sqlalchemy_mixins.session import NoSessionError  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware

from starlette.authentication import (
    AuthenticationBackend,
    SimpleUser,
    UnauthenticatedUser,
    AuthCredentials,
)

from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware  # type: ignore


class PasswordAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):

        session = request.session
        if "auth_token" in session:
            return AuthCredentials(["authenticated"]), SimpleUser(session["auth_token"])

        return AuthCredentials(["unauthenticated"]), UnauthenticatedUser()


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
    app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)


_request_id_ctx_var: ContextVar[str] = ContextVar(
    "request_id", default=None  # type: ignore
)


def get_request_id() -> str:
    return _request_id_ctx_var.get()
