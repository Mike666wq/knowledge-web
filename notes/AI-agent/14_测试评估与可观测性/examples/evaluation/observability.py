from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
import time
from typing import Any, Iterator
import uuid


SAFE_ATTRIBUTES = {
    "component", "model", "tool_name", "index_version", "outcome",
    "input_tokens", "output_tokens", "top_k", "returned_doc_ids",
}


@dataclass
class Span:
    name: str
    trace_id: str
    attributes: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0

    def set_attribute(self, name: str, value: Any) -> None:
        if name not in SAFE_ATTRIBUTES:
            raise ValueError(f"unsafe or unknown trace attribute: {name}")
        self.attributes[name] = value


@contextmanager
def start_span(name: str, trace_id: str | None = None) -> Iterator[Span]:
    span = Span(name=name, trace_id=trace_id or uuid.uuid4().hex)
    started = time.perf_counter()
    try:
        yield span
        span.set_attribute("outcome", "ok")
    except Exception:
        span.set_attribute("outcome", "error")
        raise
    finally:
        span.duration_ms = round((time.perf_counter() - started) * 1000, 3)
