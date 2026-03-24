"""Tests for govai LLM fallback classifier — API key detection."""

from unittest.mock import MagicMock, patch

from govai.llm import classify_with_llm
from govai.models import RiskTier, ToolInput


_TOOL = ToolInput(name="Test Tool")


class TestApiKeyDetection:
    """Test pre-flight API key checks in classify_with_llm."""

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_anthropic_key(self):
        """Missing ANTHROPIC_API_KEY returns UNCLEAR with actionable note."""
        result = classify_with_llm(_TOOL, model="claude-sonnet-4-6")
        assert result.risk_tier == RiskTier.UNCLEAR
        assert "API key not found" in result.notes

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_openai_key(self):
        """Missing OPENAI_API_KEY returns UNCLEAR with actionable note."""
        result = classify_with_llm(_TOOL, model="gpt-4o")
        assert result.risk_tier == RiskTier.UNCLEAR
        assert "API key not found" in result.notes
        assert "OPENAI_API_KEY" in result.notes

    @patch.dict("os.environ", {}, clear=True)
    @patch("govai.llm.litellm")
    def test_ollama_skips_key_check(self, mock_litellm):
        """Ollama models bypass the API key check entirely."""
        # Set up mock to return a valid response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='{"risk_tier": "MINIMAL"}'))
        ]
        mock_litellm.completion.return_value = mock_response
        mock_litellm.AuthenticationError = Exception

        result = classify_with_llm(_TOOL, model="ollama/llama3.2")

        # litellm.completion was called (key check was skipped)
        mock_litellm.completion.assert_called_once()
        assert result.risk_tier == RiskTier.MINIMAL

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_key_note_contains_help(self):
        """Notes field contains govai --help when key is missing."""
        result = classify_with_llm(_TOOL, model="claude-sonnet-4-6")
        assert "govai --help" in result.notes
        assert "ollama/llama3.2" in result.notes
