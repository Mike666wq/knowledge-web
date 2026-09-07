from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .agent import KnowledgeTaskAgent
from .config import Settings
from .domain import RunRequest, UserContext
from .retrieval import EvidenceGenerator, PermissionAwareRetriever, load_chunks
from .runtime import BudgetExceeded, EventRecorder
from .tools import ToolExecutor


ROOT = Path(__file__).resolve().parents[1]


class ApiRunRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    user_id: str = Field(min_length=1, max_length=128)
    roles: list[str] = Field(min_length=1, max_length=20)
    approved_fingerprint: str | None = Field(default=None, max_length=128)


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or Settings.from_env(ROOT)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        chunks = load_chunks(cfg.knowledge_path)
        app.state.agent = KnowledgeTaskAgent(
            PermissionAwareRetriever(chunks),
            EvidenceGenerator(),
            ToolExecutor(),
            top_k=cfg.rag_top_k,
            max_steps=cfg.max_steps,
            max_tool_calls=cfg.max_tool_calls,
            max_cost=cfg.max_request_cost,
        )
        yield

    app = FastAPI(title="Knowledge Task Agent", version="1.0.0", lifespan=lifespan)

    @app.exception_handler(BudgetExceeded)
    async def budget_error(_request: Request, error: BudgetExceeded):
        return JSONResponse(429, {"error": "budget_exceeded", "reason": str(error)})

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/agent/run")
    async def run(payload: ApiRunRequest, request: Request):
        # 教学简化：生产环境必须从验证后的令牌构建 UserContext。
        domain_request = RunRequest(
            question=payload.question,
            user=UserContext(payload.user_id, frozenset(payload.roles)),
            approved_fingerprint=payload.approved_fingerprint,
        )
        recorder = EventRecorder()
        async with asyncio.timeout(cfg.request_timeout):
            result = await asyncio.to_thread(request.app.state.agent.run, domain_request, recorder)
        return result

    return app


app = create_app()
