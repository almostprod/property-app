from contextvars import ContextVar

from sqlalchemy_mixins.session import NoSessionError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response

from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from structlog.contextvars import bind_contextvars


def init_app(app: Starlette):
    """
    Setup app middleware

    """
    from property_app.database.session import Session
    from property_app.database import AppBase

    @app.middleware("http")
    async def canonical_log(request: Request, call_next) -> Response:
        from property_app.logging import get_logger

        log = get_logger("property_app")
        log.info("request start")

        response = await call_next(request)

        log.info("request end")

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

        bind_contextvars(
            request_id=request_id, url=request.url.path, method=request.method
        )

        return await call_next(request)

    @app.middleware("http")
    async def clear_structlog_context(request: Request, call_next) -> Response:
        from structlog.contextvars import clear_contextvars

        clear_contextvars()

        return await call_next(request)

    app.add_middleware(ProxyHeadersMiddleware)


_request_id_ctx_var: ContextVar[str] = ContextVar(
    "request_id", default=None  # type: ignore
)


def get_request_id() -> str:
    return _request_id_ctx_var.get()
