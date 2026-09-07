import pytest

from decision_loop import StepLimitExceeded, execute, run_agent, Decision


def test_agent_finishes_with_expected_answer() -> None:
    answer, state = run_agent("查询北京温度并分类")

    assert "32℃" in answer
    assert "炎热" in answer
    assert [item["tool"] for item in state.observations] == [
        "get_temperature",
        "classify_temperature",
    ]


def test_step_limit_prevents_infinite_loop() -> None:
    with pytest.raises(StepLimitExceeded):
        run_agent("查询北京温度并分类", max_steps=1)


def test_executor_rejects_unknown_tool() -> None:
    decision = Decision("tool", "delete_everything", {})

    with pytest.raises(ValueError, match="白名单"):
        execute(decision)

