"""Tests for govai registry loader."""

from pathlib import Path

import pytest

from govai.models import ConfidenceSource, RiskTier
from govai.registry import RegistryLoader

# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"
# Path to real registry data
REGISTRY_DIR = Path(__file__).parent.parent / "registry" / "tools"


class TestRegistryLookup:
    """Test the RegistryLoader lookup functionality."""

    def setup_method(self):
        """Load the real registry for each test."""
        self.loader = RegistryLoader(registry_dir=REGISTRY_DIR)

    def test_exact_match(self):
        """Looks up tool by exact name."""
        result = self.loader.lookup("GitHub Copilot")
        assert result is not None
        assert result.tool_name == "GitHub Copilot"
        assert result.risk_tier == RiskTier.MINIMAL
        assert result.vendor == "Microsoft"

    def test_alias_match(self):
        """Looks up tool by alias."""
        result = self.loader.lookup("GH Copilot")
        assert result is not None
        assert result.tool_name == "GitHub Copilot"
        assert result.risk_tier == RiskTier.MINIMAL

    def test_case_insensitive(self):
        """Lowercase lookup finds registry entry."""
        result = self.loader.lookup("github copilot")
        assert result is not None
        assert result.tool_name == "GitHub Copilot"

    def test_case_insensitive_alias(self):
        """Lowercase alias lookup finds registry entry."""
        result = self.loader.lookup("einstein lead scoring")
        assert result is not None
        assert result.tool_name == "Salesforce Einstein Lead Scoring"

    def test_no_match(self):
        """Unknown tool returns None."""
        result = self.loader.lookup("Totally Unknown Tool XYZ")
        assert result is None

    def test_confidence_source(self):
        """Registry results have REGISTRY_MATCH confidence."""
        result = self.loader.lookup("GitHub Copilot")
        assert result is not None
        assert result.confidence_source == ConfidenceSource.REGISTRY_MATCH

    def test_high_risk_tool(self):
        """Known HIGH risk tool returns correct tier."""
        result = self.loader.lookup("Salesforce Einstein Lead Scoring")
        assert result is not None
        assert result.risk_tier == RiskTier.HIGH

    def test_limited_risk_tool(self):
        """Known LIMITED risk tool returns correct tier."""
        result = self.loader.lookup("Microsoft 365 Copilot")
        assert result is not None
        assert result.risk_tier == RiskTier.LIMITED

    def test_unclear_risk_tool(self):
        """Known UNCLEAR risk tool returns correct tier."""
        result = self.loader.lookup("Azure OpenAI Service")
        assert result is not None
        assert result.risk_tier == RiskTier.UNCLEAR

    def test_whitespace_stripped(self):
        """Leading/trailing whitespace is stripped."""
        result = self.loader.lookup("  GitHub Copilot  ")
        assert result is not None
        assert result.tool_name == "GitHub Copilot"

    def test_empty_string_returns_none(self):
        """Empty string returns None."""
        result = self.loader.lookup("")
        assert result is None

    def test_result_has_ai_features(self):
        """Registry result includes ai_features from YAML."""
        result = self.loader.lookup("GitHub Copilot")
        assert result is not None
        assert len(result.ai_features) > 0

    def test_result_has_raw_input(self):
        """Registry result includes the original raw_input."""
        result = self.loader.lookup("GitHub Copilot")
        assert result is not None
        assert result.raw_input.name == "GitHub Copilot"


class TestMalformedYaml:
    """Test error handling for malformed YAML files."""

    def test_malformed_yaml(self):
        """Malformed YAML raises ValueError with filename."""
        with pytest.raises(ValueError, match="broken.yaml"):
            RegistryLoader(registry_dir=FIXTURES_DIR)
