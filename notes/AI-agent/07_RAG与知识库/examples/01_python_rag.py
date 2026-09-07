"""纯 Python 教学 RAG：哈希向量检索 + 有依据的抽取式回答。"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class SourceDocument:
    document_id: str
    source: str
    text: str


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    source: str
    start: int
    text: str


@dataclass(frozen=True)
class SearchHit:
    chunk: Chunk
    score: float


def split_document(
    document: SourceDocument, *, chunk_size: int = 80, overlap: int = 20
) -> list[Chunk]:
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap 必须满足 0 <= overlap < chunk_size")
    chunks: list[Chunk] = []
    step = chunk_size - overlap
    for index, start in enumerate(range(0, len(document.text), step)):
        text = document.text[start : start + chunk_size].strip()
        if text:
            chunks.append(
                Chunk(
                    chunk_id=f"{document.document_id}#{index}",
                    document_id=document.document_id,
                    source=document.source,
                    start=start,
                    text=text,
                )
            )
        if start + chunk_size >= len(document.text):
            break
    return chunks


def text_features(text: str) -> list[str]:
    normalized = re.sub(r"\s+", "", text.lower())
    chinese = [char for char in normalized if "\u4e00" <= char <= "\u9fff"]
    bigrams = ["".join(chinese[i : i + 2]) for i in range(len(chinese) - 1)]
    ascii_words = re.findall(r"[a-z0-9_-]+", normalized)
    return chinese + bigrams + ascii_words


def embed(text: str, *, dimensions: int = 256) -> list[float]:
    vector = [0.0] * dimensions
    for feature in text_features(text):
        digest = hashlib.sha256(feature.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


class InMemoryIndex:
    def __init__(self, chunks: Iterable[Chunk]) -> None:
        self.entries = [(chunk, embed(chunk.text)) for chunk in chunks]

    def search(self, query: str, *, k: int = 3) -> list[SearchHit]:
        query_vector = embed(query)
        hits = [
            SearchHit(chunk=chunk, score=cosine(query_vector, vector))
            for chunk, vector in self.entries
        ]
        return sorted(hits, key=lambda item: item.score, reverse=True)[:k]


def answer_with_evidence(
    question: str, hits: list[SearchHit], *, min_score: float = 0.10
) -> str:
    accepted = [hit for hit in hits if hit.score >= min_score]
    if not accepted:
        return "证据不足，无法依据当前知识库回答。"
    evidence = "\n".join(
        f"- [{hit.chunk.chunk_id}] {hit.chunk.text}" for hit in accepted
    )
    return f"问题：{question}\n依据当前检索结果：\n{evidence}"


def main() -> None:
    documents = [
        SourceDocument(
            "agent-policy",
            "agent_policy.md",
            "Agent 每次任务最多执行 8 个步骤。达到上限后必须停止，并返回预算超限状态。高风险写操作必须经过人工确认。",
        ),
        SourceDocument(
            "rag-guide",
            "rag_guide.md",
            "RAG 的离线流程负责切分和建立索引。在线流程接收问题，执行检索，再让模型基于证据回答。",
        ),
        SourceDocument(
            "memory-guide",
            "memory_guide.md",
            "短期记忆属于一个对话线程。长期记忆可以跨线程保存用户偏好，并应按用户命名空间隔离。",
        ),
    ]
    chunks = [chunk for doc in documents for chunk in split_document(doc)]
    index = InMemoryIndex(chunks)

    question = "Agent 最多能运行多少个步骤？"
    hits = index.search(question, k=2)
    for hit in hits:
        print(f"score={hit.score:.3f} source={hit.chunk.chunk_id}")
    print(answer_with_evidence(question, hits))


if __name__ == "__main__":
    main()
