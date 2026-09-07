from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .agent import AgentService, MockModelClient
from .config import Settings
from .logging_config import configure_logging, request_id_var
from .retry import RetryPolicy, TransientUpstreamError


class AnswerRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class AnswerResponse(BaseModel):
    answer: str
    model: str
    request_id: str


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or Settings.from_env()
    configure_logging(cfg.log_level)
    logger = logging.getLogger("delivery_service")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.agent = AgentService(
            MockModelClient(),
            model=cfg.model,
            request_timeout=cfg.request_timeout,
            max_concurrency=cfg.max_concurrency,
            retry_policy=RetryPolicy(max_retries=cfg.max_retries),
        )
        app.state.ready = True
        yield
        app.state.ready = False

    app = FastAPI(title="Delivery Agent", version="1.0.0", lifespan=lifespan)

    @app.middleware("http")
    async def correlate_request(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_var.set(request_id[:128])
        started = time.perf_counter()
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            logger.info(
                "request_finished",
                extra={"duration_ms": round((time.perf_counter() - started) * 1000, 2)},
            )
            request_id_var.reset(token)

    @app.exception_handler(asyncio.TimeoutError)
    async def timeout_handler(_request: Request, _error: asyncio.TimeoutError):
        return JSONResponse(status_code=504, content={"error": "agent_timeout"})

    @app.exception_handler(TransientUpstreamError)
    async def upstream_handler(_request: Request, _error: TransientUpstreamError):
        return JSONResponse(status_code=503, content={"error": "upstream_unavailable"})

    @app.get("/live")
    async def live() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/ready")
    async def ready(request: Request):
        if not getattr(request.app.state, "ready", False):
            return JSONResponse(status_code=503, content={"status": "not_ready"})
        return {"status": "ready"}

    @app.post("/v1/answer", response_model=AnswerResponse)
    async def answer(payload: AnswerRequest, request: Request) -> AnswerResponse:
        result = await request.app.state.agent.answer(payload.question)
        return AnswerResponse(
            answer=result.text,
            model=result.model,
            request_id=request_id_var.get(),
        )

    return app


app = create_app()
