from __future__ import annotations

from dataclasses import dataclass
import math
import re
from statistics import mean
from typing import Any, Iterable


def _unique(items: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(items))


def recall_at_k(retrieved: list[str], relevant: list[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    expected = set(relevant)
    if not expected:
        return 1.0
    found = set(_unique(retrieved)[:k])
    return len(found & expected) / len(expected)


def precision_at_k(retrieved: list[str], relevant: list[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    selected = _unique(retrieved)[:k]
    if not selected:
        return 1.0 if not relevant else 0.0
    return len(set(selected) & set(relevant)) / len(selected)


def reciprocal_rank(retrieved: list[str], relevant: list[str]) -> float:
    expected = set(relevant)
    if not expected:
        return 1.0
    for rank, doc_id in enumerate(_unique(retrieved), start=1):
        if doc_id in expected:
            return 1.0 / rank
    return 0.0


def normalize_text(text: str) -> str:
    return re.sub(r"[\W_]+", "", text.casefold(), flags=re.UNICODE)


def fact_coverage(answer: str, expected_facts: list[str]) -> float:
    if not expected_facts:
        return 1.0
    normalized = normalize_text(answer)
    covered = sum(normalize_text(fact) in normalized for fact in expected_facts)
    return covered / len(expected_facts)


def tool_name_accuracy(actual: str | None, expected: str | None) -> float:
    return float(actual == expected)


def argument_exact_match(actual: Any, expected: Any) -> float:
    return float(actual == expected)


def percentile(values: list[float], probability: float) -> float:
    if not values:
        return 0.0
    if not 0 <= probability <= 1:
        raise ValueError("probability must be in [0, 1]")
    ordered = sorted(values)
    index = max(0, math.ceil(probability * len(ordered)) - 1)
    return ordered[index]


@dataclass(frozen=True)
class EvaluationSummary:
    cases: int
    recall_at_3: float
    precision_at_3: float
    mrr: float
    fact_coverage: float
    tool_accuracy: float
    argument_accuracy: float
    latency_p95_ms: float
    total_cost: float


def summarize(cases: list[tuple[dict[str, Any], dict[str, Any]]]) -> EvaluationSummary:
    if not cases:
        return EvaluationSummary(0, 0, 0, 0, 0, 0, 0, 0, 0)
    recalls, precisions, ranks, facts, tools, arguments = [], [], [], [], [], []
    latencies, costs = [], []
    for expected, actual in cases:
        retrieved = actual.get("retrieved_doc_ids", [])
        relevant = expected.get("relevant_doc_ids", [])
        recalls.append(recall_at_k(retrieved, relevant, 3))
        precisions.append(precision_at_k(retrieved, relevant, 3))
        ranks.append(reciprocal_rank(retrieved, relevant))
        facts.append(fact_coverage(actual.get("answer", ""), expected.get("expected_facts", [])))
        tools.append(tool_name_accuracy(actual.get("tool"), expected.get("expected_tool")))
        arguments.append(argument_exact_match(actual.get("arguments"), expected.get("expected_arguments")))
        latencies.append(float(actual.get("latency_ms", 0)))
        costs.append(float(actual.get("cost", 0)))
    return EvaluationSummary(
        cases=len(cases),
        recall_at_3=mean(recalls),
        precision_at_3=mean(precisions),
        mrr=mean(ranks),
        fact_coverage=mean(facts),
        tool_accuracy=mean(tools),
        argument_accuracy=mean(arguments),
        latency_p95_ms=percentile(latencies, 0.95),
        total_cost=sum(costs),
    )
