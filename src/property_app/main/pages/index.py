import json
import asyncio
import typing

from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException
from starlette.requests import Request, empty_receive, empty_send
from starlette.responses import PlainTextResponse
from starlette.types import Receive, Scope, Send
from starlette.responses import Response, JSONResponse

from ..router import templates


class InertiaRequest(Request):
    def __init__(
        self, scope: Scope, receive: Receive = empty_receive, send: Send = empty_send
    ):
        super().__init__(scope, receive=receive, send=send)
        self.is_inertia_request = self.headers.get("X-Inertia", False)
        self.inertia_asset_version = self.headers.get("X-Inertia-Version", None)


class InertiaHTTPEndpoint:

    __inertia_component__: typing.Optional[str] = None

    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:
        assert scope["type"] == "http"
        self.scope = scope
        self.receive = receive
        self.send = send
        self.component = self.__inertia_component__
        if not self.component:
            self.component = self.__class__.__name__

    def __await__(self) -> typing.Generator:
        return self.dispatch().__await__()

    async def _handle_html(self, request, context):
        return templates.TemplateResponse(
            "index.html", {"request": request, "inertia_context": json.dumps(context)},
        )

    async def _handle_inertia(self, request, context):
        return JSONResponse(context)

    def _handle(self, request) -> typing.Awaitable[dict]:
        handler_name = "get" if request.method == "HEAD" else request.method.lower()
        handler = getattr(self, handler_name, self.method_not_allowed)

        is_async = asyncio.iscoroutinefunction(handler)
        if is_async:
            return handler(request)

        return run_in_threadpool(handler, request)

    def _inertia_context(self, request, props):
        return {
            "component": self.component,
            "props": props,
            "url": str(request.url),
            "version": "dev",
        }

    async def dispatch(self) -> None:
        request = InertiaRequest(self.scope, receive=self.receive)
        props = await self._handle(request)
        context = self._inertia_context(request, props)

        if request.is_inertia_request:
            response = await self._handle_inertia(request, context)
        else:
            response = await self._handle_html(request, context)

        await response(self.scope, self.receive, self.send)

    async def method_not_allowed(self, request: Request) -> Response:
        if "app" in self.scope:
            raise HTTPException(status_code=405)

        return PlainTextResponse("Method Not Allowed", status_code=405)


class Index(InertiaHTTPEndpoint):
    def get(self, request: Request):
        content = request.query_params["content"]
        return {"pageContent": content}


# def Index(InertiaEndpoint):
#     __component__ = "Index"
