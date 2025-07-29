import logging

from starlette.types import ASGIApp, Receive, Scope, Send


class CatchExceptionsMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            await self.app(scope, receive, send)
        except Exception as e:
            logging.exception(f"An exception occurred: {e}")
