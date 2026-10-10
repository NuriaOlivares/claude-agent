import pytest
from unittest.mock import MagicMock, patch


def test_ask_claude_returns_string(mocker):
    """
    Test that ask_claude calls the Anthropic API and returns
    the text content as a string.

    We mock the Anthropic client so no real API call is made.
    """
    # Create a fake response that looks like what Claude API returns
    fake_response = MagicMock()
    fake_response.content = [MagicMock(text="Hello from Claude")]

    # Patch the Anthropic client's messages.create method
    # This replaces the real API call with our fake response
    with patch("claude_client.client") as mock_client:
        mock_client.messages.create.return_value = fake_response

        # Now import and call the real function
        from claude_client import ask_claude
        result = ask_claude(
            system_prompt="You are a helpful assistant.",
            user_message="Say hello."
        )

    # Assert the function returned the text from the fake response
    assert result == "Hello from Claude"
    assert isinstance(result, str)


def test_ask_claude_passes_correct_model(mocker):
    """
    Test that ask_claude always uses claude-sonnet-4-6.
    We never want it silently switching to a more expensive model.
    """
    fake_response = MagicMock()
    fake_response.content = [MagicMock(text="response")]

    with patch("claude_client.client") as mock_client:
        mock_client.messages.create.return_value = fake_response

        from claude_client import ask_claude
        ask_claude("system", "user")

        # Check the model argument that was passed to the API
        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs["model"] == "claude-sonnet-4-6"


def test_ask_claude_raises_if_no_api_key():
    """
    Test that the module raises a clear error if the API key is missing.
    Better to fail loudly than silently.
    """
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": ""}):
        with pytest.raises(Exception):
            # Re-importing triggers the key check at module level
            import importlib
            import claude_client
            importlib.reload(claude_client)