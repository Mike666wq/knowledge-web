import pytest

from settings import ConfigurationError, Settings


def test_settings_from_valid_mapping() -> None:
    settings = Settings.from_env(
        {
            "OPENAI_API_KEY": "test-key",
            "OPENAI_BASE_URL": "https://provider.example/v1",
            "LLM_MODEL": "test-model",
            "REQUEST_TIMEOUT": "15",
        }
    )

    assert settings.model == "test-model"
    assert settings.timeout == 15.0
    assert "test-key" not in str(settings.safe_summary())


def test_missing_key_is_rejected() -> None:
    with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
        Settings.from_env({"LLM_MODEL": "test-model"})


@pytest.mark.parametrize("value", ["abc", "0", "601"])
def test_invalid_timeout_is_rejected(value: str) -> None:
    with pytest.raises(ConfigurationError, match="REQUEST_TIMEOUT"):
        Settings.from_env(
            {
                "OPENAI_API_KEY": "test-key",
                "LLM_MODEL": "test-model",
                "REQUEST_TIMEOUT": value,
            }
        )

