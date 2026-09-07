from __future__ import annotations

import json
from pathlib import Path
import re

from .domain import Chunk, Citation, UserContext


INJECTION_PATTERNS = (
    re.compile(r"ignore (all |the )?(previous|prior) instructions", re.I),
    re.compile(r"忽略(之前|以上|所有).{0,8}(指令|规则)"),
    re.compile(r"(export|reveal|显示|导出).{0,12}(secret|key|密钥|凭据)", re.I),
)


def load_chunks(path: Path) -> list[Chunk]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        Chunk(
            doc_id=item["doc_id"],
            chunk_id=item["chunk_id"],
            title=item["title"],
            text=item["text"],
            roles=frozenset(item["roles"]),
        )
        for item in data
    ]


def is_suspicious(text: str) -> bool:
    return any(pattern.search(text) for pattern in INJECTION_PATTERNS)


def _score(question: str, text: str) -> float:
    query_chars = {char for char in question.casefold() if not char.isspace()}
    text_chars = {char for char in text.casefold() if not char.isspace()}
    if not query_chars:
        return 0.0
    return len(query_chars & text_chars) / len(query_chars)


class PermissionAwareRetriever:
    def __init__(self, chunks: list[Chunk]) -> None:
        self._chunks = chunks

    def retrieve(self, question: str, user: UserContext, top_k: int) -> list[Chunk]:
        authorized = [chunk for chunk in self._chunks if chunk.roles & user.roles]
        safe = [chunk for chunk in authorized if not is_suspicious(chunk.text)]
        ranked = sorted(safe, key=lambda item: _score(question, item.text), reverse=True)
        return [chunk for chunk in ranked if _score(question, chunk.text) > 0][:top_k]


class EvidenceGenerator:
    """Deterministic adapter. Replace with a structured-output LLM in production."""

    def generate(self, question: str, chunks: list[Chunk]) -> tuple[str, tuple[Citation, ...]]:
        if not chunks:
            return "现有授权资料中没有足够证据回答这个问题。", ()
        evidence = "\n".join(f"- {chunk.text} [{chunk.chunk_id}]" for chunk in chunks)
        answer = f"根据授权知识库，相关证据如下：\n{evidence}"
        citations = tuple(Citation(c.doc_id, c.chunk_id, c.title) for c in chunks)
        return answer, citations
