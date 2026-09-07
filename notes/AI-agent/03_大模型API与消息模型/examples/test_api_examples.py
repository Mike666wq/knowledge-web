from types import SimpleNamespace

from client_factory import ModelConfig, build_client
from conversation import Conversation
from single_turn import ask_once
from streaming_chat import iter_text_chunks


class FakeCompletions:
    def __init__(self, answer: str = "测试回答") -> None:
        self.answer = answer
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[
                SimpleNamespace(message=SimpleNamespace(content=self.answer))
            ]
        )


class FakeClient:
    def __init__(self, answer: str = "测试回答") -> None:
        self.chat = SimpleNamespace(completions=FakeCompletions(answer))


CONFIG = ModelConfig(
    api_key="test-key",
    model="test-model",
    base_url="https://provider.example/v1",
    timeout=10,
)


def test_build_client_passes_configuration_without_network() -> None:
    captured = {}

    def fake_constructor(**kwargs):
        captured.update(kwargs)
        return object()

    build_client(CONFIG, client_cls=fake_constructor)

    assert captured["api_key"] == "test-key"
    assert captured["base_url"] == "https://provider.example/v1"
    assert captured["timeout"] == 10


def test_single_turn_builds_role_separated_messages() -> None:
    client = FakeClient("Agent 是动态选择行动的系统。")

    answer = ask_once(client, CONFIG, "什么是 Agent？")

    call = client.chat.completions.calls[0]
    assert answer.startswith("Agent")
    assert call["model"] == "test-model"
    assert [message["role"] for message in call["messages"]] == [
        "system",
        "user",
    ]


def test_conversation_sends_previous_history() -> None:
    client = FakeClient()
    conversation = Conversation(client, CONFIG, "系统规则")

    conversation.ask("第一问")
    conversation.ask("第二问")

    second_call = client.chat.completions.calls[1]
    assert [item["role"] for item in second_call["messages"]] == [
        "system",
        "user",
        "assistant",
        "user",
    ]


def test_stream_parser_ignores_empty_chunks() -> None:
    chunks = [
        SimpleNamespace(choices=[]),
        SimpleNamespace(
            choices=[SimpleNamespace(delta=SimpleNamespace(content=None))]
        ),
        SimpleNamespace(
            choices=[SimpleNamespace(delta=SimpleNamespace(content="你"))]
        ),
        SimpleNamespace(
            choices=[SimpleNamespace(delta=SimpleNamespace(content="好"))]
        ),
    ]

    assert "".join(iter_text_chunks(chunks)) == "你好"

