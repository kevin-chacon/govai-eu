"""Tests for govai classifier and LLM fallback."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from govai.models import (
    ClassificationResult,
    ConfidenceSource,
    RiskTier,
    ToolInput,
)
from govai.classifier import classify_tool, parse_input_file
from govai.llm import classify_with_llm, _parse_response

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestClassifyTool:
    """Test the classify_tool orchestration."""

    def test_registry_hit(self, mocker):
        """Known tool uses registry, LLM not called."""
        tool = ToolInput(name="GitHub Copilot")
        mock_llm = mocker.patch("govai.classifier.llm.classify_with_llm")

        result = classify_tool(tool, model="test-model", no_llm=False)

        assert result.tool_name == "GitHub Copilot"
        assert result.confidence_source == ConfidenceSource.REGISTRY_MATCH
        mock_llm.assert_not_called()

    def test_llm_fallback(self, mocker):
        """Unknown tool calls LLM when no_llm=False."""
        tool = ToolInput(name="Unknown AI Tool XYZ")
        mock_result = ClassificationResult(
            tool_name="Unknown AI Tool XYZ",
            risk_tier=RiskTier.MINIMAL,
            confidence_source=ConfidenceSource.INFERRED,
            raw_input=tool,
        )
        mocker.patch("govai.classifier.registry.lookup", return_value=None)
        mock_llm = mocker.patch(
            "govai.classifier.llm.classify_with_llm",
            return_value=mock_result,
        )

        result = classify_tool(tool, model="test-model", no_llm=False)

        assert result.risk_tier == RiskTier.MINIMAL
        assert result.confidence_source == ConfidenceSource.INFERRED
        mock_llm.assert_called_once_with(tool, "test-model")

    def test_no_llm_flag(self, mocker):
        """Unknown tool returns UNCLEAR when no_llm=True, LLM not called."""
        tool = ToolInput(name="Unknown AI Tool XYZ")
        mocker.patch("govai.classifier.registry.lookup", return_value=None)
        mock_llm = mocker.patch("govai.classifier.llm.classify_with_llm")

        result = classify_tool(tool, model="test-model", no_llm=True)

        assert result.risk_tier == RiskTier.UNCLEAR
        assert "Not in registry" in result.notes
        mock_llm.assert_not_called()


class TestParseInputFile:
    """Test file parsing for CSV and plain text."""

    def test_parse_csv(self):
        """Sample CSV parsed to list of ToolInput."""
        tools = parse_input_file(FIXTURES_DIR / "sample_tools.csv")
        assert len(tools) > 0
        assert all(isinstance(t, ToolInput) for t in tools)
        # First tool should be Salesforce Einstein
        assert tools[0].name == "Salesforce Einstein"
        assert tools[0].description == "Lead scoring and opportunity insights"

    def test_parse_txt(self):
        """Plain text file parsed to list of ToolInput."""
        tools = parse_input_file(FIXTURES_DIR / "sample_tools.txt")
        assert len(tools) > 0
        assert all(isinstance(t, ToolInput) for t in tools)
        # Text files don't have descriptions
        assert all(t.description is None for t in tools)

    def test_skip_empty_lines(self):
        """Empty lines and # comments are ignored."""
        tools = parse_input_file(FIXTURES_DIR / "sample_tools.txt")
        tool_names = [t.name for t in tools]
        # No empty strings or comments in results
        assert all(name.strip() for name in tool_names)
        assert all(not name.startswith("#") for name in tool_names)

    def test_file_not_found(self):
        """FileNotFoundError raised with clear message."""
        with pytest.raises(FileNotFoundError, match="nonexistent_file.csv"):
            parse_input_file(Path("nonexistent_file.csv"))

    def test_csv_with_descriptions(self):
        """CSV second column becomes description."""
        tools = parse_input_file(FIXTURES_DIR / "sample_tools.csv")
        has_desc = any(t.description is not None for t in tools)
        assert has_desc, "At least one CSV tool should have a description"

    def test_txt_tool_count(self):
        """Text file has expected number of tools (comments/blanks excluded)."""
        tools = parse_input_file(FIXTURES_DIR / "sample_tools.txt")
        # sample_tools.txt has 5 actual tool names (not comments or blanks)
        assert len(tools) == 5


class TestLLMResponseParsing:
    """Test LLM response parsing without calling real APIs."""

    def test_parse_valid_json(self):
        """Valid JSON response parsed correctly."""
        tool = ToolInput(name="Test Tool")
        raw = '{"risk_tier": "HIGH", "ai_features": ["feature1"], "decision_scope": "scope", "data_categories": ["data"], "obligations": ["ob1"], "missing_docs": ["doc1"], "notes": "note", "vendor": "Vendor"}'
        result = _parse_response(raw, tool)
        assert result.risk_tier == RiskTier.HIGH
        assert result.confidence_source == ConfidenceSource.INFERRED
        assert result.vendor == "Vendor"

    def test_parse_json_with_code_fences(self):
        """JSON wrapped in markdown code fences is handled."""
        tool = ToolInput(name="Test Tool")
        raw = '```json\n{"risk_tier": "MINIMAL", "ai_features": [], "decision_scope": null, "data_categories": [], "obligations": [], "missing_docs": [], "notes": null, "vendor": null}\n```'
        result = _parse_response(raw, tool)
        assert result.risk_tier == RiskTier.MINIMAL

    def test_parse_invalid_json(self):
        """Invalid JSON returns UNCLEAR result."""
        tool = ToolInput(name="Test Tool")
        raw = "this is not json at all"
        result = _parse_response(raw, tool)
        assert result.risk_tier == RiskTier.UNCLEAR
        assert "Failed to parse" in result.notes

    def test_classify_with_llm_api_error(self, mocker):
        """API error returns UNCLEAR result, never raises."""
        tool = ToolInput(name="Test Tool")
        mocker.patch(
            "govai.llm.litellm.completion",
            side_effect=Exception("API connection failed"),
        )
        result = classify_with_llm(tool, model="test-model")
        assert result.risk_tier == RiskTier.UNCLEAR
        assert "failed" in result.notes.lower()

    def test_classify_with_llm_success(self, mocker):
        """Successful LLM call returns parsed result."""
        tool = ToolInput(name="Test Tool", description="An AI tool")
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            '{"risk_tier": "LIMITED", "ai_features": ["chat"], '
            '"decision_scope": null, "data_categories": ["text"], '
            '"obligations": ["transparency"], "missing_docs": [], '
            '"notes": null, "vendor": "TestCo"}'
        )
        mocker.patch("govai.llm.litellm.completion", return_value=mock_response)

        result = classify_with_llm(tool, model="test-model")
        assert result.risk_tier == RiskTier.LIMITED
        assert result.confidence_source == ConfidenceSource.INFERRED
        assert result.vendor == "TestCo"
