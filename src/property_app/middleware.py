from contextvars import ContextVar

from sqlalchemy_mixins.session import NoSessionError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response

from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware


def init_app(app: Starlette):
    """
    Setup app middleware

    """
    from property_app.database.session import Session
    from property_app.database import AppBase

    @app.middleware("http")
    async def clear_structlog_context(request: Request, call_next) -> Response:
        from structlog.contextvars import clear_contextvars

        clear_contextvars()

        return await call_next(request)

    @app.middleware("http")
    async def inject_request_id(request: Request, call_next) -> Response:
        import uuid
        from structlog.contextvars import bind_contextvars

        request_id = str(uuid.uuid4())

        _request_id_ctx_var.set(request_id)
        request.state.request_id = request_id

        bind_contextvars(request_id=request_id)

        return await call_next(request)

    app.add_middleware(ProxyHeadersMiddleware)

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


_request_id_ctx_var: ContextVar[str] = ContextVar(
    "request_id", default=None  # type: ignore
)


def get_request_id() -> str:
    return _request_id_ctx_var.get()
