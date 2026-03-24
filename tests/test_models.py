"""Tests for govai data models."""

import json
from datetime import datetime

from govai.models import (
    ClassificationResult,
    ConfidenceSource,
    InventoryReport,
    RiskTier,
    ToolInput,
)


class TestRiskTiers:
    """Test all risk tier values exist and behave correctly."""

    def test_all_risk_tiers(self):
        """Create a ClassificationResult for each RiskTier."""
        tool = ToolInput(name="Test Tool")
        for tier in RiskTier:
            result = ClassificationResult(
                tool_name="Test Tool",
                risk_tier=tier,
                confidence_source=ConfidenceSource.REGISTRY_MATCH,
                raw_input=tool,
            )
            assert result.risk_tier == tier

    def test_risk_tier_values(self):
        """Risk tier string values match EU AI Act language."""
        assert RiskTier.UNACCEPTABLE.value == "UNACCEPTABLE"
        assert RiskTier.HIGH.value == "HIGH"
        assert RiskTier.LIMITED.value == "LIMITED"
        assert RiskTier.MINIMAL.value == "MINIMAL"
        assert RiskTier.UNCLEAR.value == "UNCLEAR"


class TestConfidenceSource:
    """Test confidence source enum."""

    def test_values(self):
        assert ConfidenceSource.REGISTRY_MATCH.value == "registry_match"
        assert ConfidenceSource.INFERRED.value == "inferred"


class TestSerialisation:
    """Test model serialisation to JSON."""

    def test_classification_result_to_json(self):
        """model.model_dump_json() produces valid JSON."""
        tool = ToolInput(name="Salesforce Einstein", description="Lead scoring")
        result = ClassificationResult(
            tool_name="Salesforce Einstein",
            vendor="Salesforce",
            risk_tier=RiskTier.HIGH,
            confidence_source=ConfidenceSource.REGISTRY_MATCH,
            ai_features=["Lead scoring", "Opportunity insights"],
            decision_scope="Autonomous lead routing",
            data_categories=["Customer data", "Sales data"],
            obligations=["Conformity assessment", "Risk management system"],
            missing_docs=["Technical documentation", "Data governance policy"],
            notes="Risk tier depends on specific module configuration",
            raw_input=tool,
        )
        json_str = result.model_dump_json()
        parsed = json.loads(json_str)
        assert parsed["tool_name"] == "Salesforce Einstein"
        assert parsed["risk_tier"] == "HIGH"
        assert parsed["confidence_source"] == "registry_match"

    def test_inventory_report_to_json(self):
        """InventoryReport serialises with enum string values."""
        tool = ToolInput(name="Test")
        result = ClassificationResult(
            tool_name="Test",
            risk_tier=RiskTier.MINIMAL,
            confidence_source=ConfidenceSource.INFERRED,
            raw_input=tool,
        )
        report = InventoryReport(
            generated_at=datetime(2026, 3, 23, 12, 0, 0),
            input_file="tools.csv",
            tool_count=1,
            risk_summary={RiskTier.MINIMAL: 1},
            results=[result],
        )
        json_str = report.model_dump_json(indent=2)
        parsed = json.loads(json_str)
        assert parsed["tool_count"] == 1
        assert parsed["results"][0]["risk_tier"] == "MINIMAL"


class TestOptionalFields:
    """Test that optional fields default correctly."""

    def test_optional_fields_default_to_none(self):
        """vendor, decision_scope, and notes default to None."""
        tool = ToolInput(name="Test Tool")
        result = ClassificationResult(
            tool_name="Test Tool",
            risk_tier=RiskTier.MINIMAL,
            confidence_source=ConfidenceSource.INFERRED,
            raw_input=tool,
        )
        assert result.vendor is None
        assert result.decision_scope is None
        assert result.notes is None

    def test_list_fields_default_to_empty(self):
        """List fields default to empty lists."""
        tool = ToolInput(name="Test Tool")
        result = ClassificationResult(
            tool_name="Test Tool",
            risk_tier=RiskTier.MINIMAL,
            confidence_source=ConfidenceSource.INFERRED,
            raw_input=tool,
        )
        assert result.ai_features == []
        assert result.data_categories == []
        assert result.obligations == []
        assert result.missing_docs == []

    def test_tool_input_description_optional(self):
        """ToolInput.description defaults to None."""
        tool = ToolInput(name="Test")
        assert tool.description is None
