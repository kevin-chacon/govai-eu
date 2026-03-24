"""Tests for govai report generation."""

import json
from datetime import datetime, timezone

from govai.models import (
    ClassificationResult,
    ConfidenceSource,
    InventoryReport,
    RiskTier,
    ToolInput,
)
from govai.reporter import to_html, to_json, to_markdown, write_reports


def _make_report() -> InventoryReport:
    """Create a sample report for testing."""
    tools = [
        ClassificationResult(
            tool_name="Salesforce Einstein Lead Scoring",
            vendor="Salesforce",
            risk_tier=RiskTier.HIGH,
            confidence_source=ConfidenceSource.REGISTRY_MATCH,
            ai_features=["Predictive lead scoring", "Lead routing"],
            decision_scope="Autonomous lead scoring and routing",
            data_categories=["Lead data", "Sales data"],
            obligations=["Conformity assessment", "Risk management"],
            missing_docs=["Conformity assessment report"],
            notes="HIGH risk due to autonomous routing",
            raw_input=ToolInput(name="Salesforce Einstein"),
        ),
        ClassificationResult(
            tool_name="GitHub Copilot",
            vendor="Microsoft",
            risk_tier=RiskTier.MINIMAL,
            confidence_source=ConfidenceSource.REGISTRY_MATCH,
            ai_features=["Code completion"],
            decision_scope="Suggests code; developer reviews",
            data_categories=["Source code"],
            obligations=[],
            missing_docs=[],
            raw_input=ToolInput(name="GitHub Copilot"),
        ),
        ClassificationResult(
            tool_name="HubSpot ChatSpot",
            vendor="HubSpot",
            risk_tier=RiskTier.LIMITED,
            confidence_source=ConfidenceSource.REGISTRY_MATCH,
            ai_features=["Conversational AI"],
            decision_scope=None,
            data_categories=["CRM data"],
            obligations=["Transparency disclosure"],
            missing_docs=["AI disclosure notice"],
            raw_input=ToolInput(name="HubSpot ChatSpot"),
        ),
        ClassificationResult(
            tool_name="Custom Internal Tool",
            risk_tier=RiskTier.UNCLEAR,
            confidence_source=ConfidenceSource.INFERRED,
            notes="LLM classification failed",
            raw_input=ToolInput(name="Custom Internal Tool"),
        ),
    ]

    return InventoryReport(
        generated_at=datetime(2026, 3, 23, 12, 0, 0, tzinfo=timezone.utc),
        input_file="test_tools.csv",
        tool_count=4,
        risk_summary={
            RiskTier.HIGH: 1,
            RiskTier.LIMITED: 1,
            RiskTier.MINIMAL: 1,
            RiskTier.UNCLEAR: 1,
        },
        results=tools,
    )


class TestMarkdownReport:
    """Test markdown report generation."""

    def test_markdown_contains_required_sections(self):
        """All five structural sections are present."""
        report = _make_report()
        md = to_markdown(report)

        assert "# govai — AI System Inventory Report" in md
        assert "**Generated:**" in md
        assert "## Risk Summary" in md
        assert "| Risk Tier |" in md
        # Check at least one tool section exists
        assert "## HIGH —" in md

    def test_markdown_high_risk_first(self):
        """HIGH risk tools appear before MINIMAL in the output."""
        report = _make_report()
        md = to_markdown(report)

        high_pos = md.index("Salesforce Einstein Lead Scoring")
        minimal_pos = md.index("GitHub Copilot")
        assert high_pos < minimal_pos

    def test_markdown_tier_ordering(self):
        """Risk tiers appear in order: HIGH \u2192 LIMITED \u2192 MINIMAL \u2192 UNCLEAR in per-tool sections."""
        report = _make_report()
        md = to_markdown(report)

        # Use full tool headings to find per-tool sections (not reference sections)
        high_pos = md.index("Salesforce Einstein Lead Scoring (Salesforce)")
        limited_pos = md.index("HubSpot ChatSpot (HubSpot)")
        minimal_pos = md.index("GitHub Copilot (Microsoft)")
        unclear_pos = md.index("Custom Internal Tool")

        assert high_pos < limited_pos < minimal_pos < unclear_pos

    def test_disclaimer_present(self):
        """Footer disclaimer text appears in markdown output."""
        report = _make_report()
        md = to_markdown(report)

        assert "starting point for EU AI Act compliance review" in md
        assert "not a legal opinion" in md
        assert "govai is open source" in md

    def test_markdown_contains_tool_details(self):
        """Tool sections contain confidence, features, obligations."""
        report = _make_report()
        md = to_markdown(report)

        assert "**Confidence:** registry_match" in md
        assert "found in govai-eu registry" in md
        assert "**AI Features:**" in md
        assert "**Decision Scope:**" in md
        assert "**EU AI Act Obligations:**" in md

    def test_markdown_vendor_in_heading(self):
        """Vendor name appears in tool heading when present."""
        report = _make_report()
        md = to_markdown(report)

        assert "(Salesforce)" in md
        assert "(Microsoft)" in md

    def test_markdown_risk_summary_table(self):
        """Risk summary table has correct counts and meanings."""
        report = _make_report()
        md = to_markdown(report)

        assert "| HIGH | 1 |" in md
        assert "| MINIMAL | 1 |" in md
        assert "| Meaning |" in md


class TestJsonReport:
    """Test JSON report generation."""

    def test_json_valid(self):
        """to_json() output is valid JSON."""
        report = _make_report()
        json_str = to_json(report)
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)

    def test_json_roundtrip(self):
        """Deserialise JSON back to InventoryReport."""
        report = _make_report()
        json_str = to_json(report)
        restored = InventoryReport.model_validate_json(json_str)
        assert restored.tool_count == report.tool_count
        assert len(restored.results) == len(report.results)
        assert restored.results[0].tool_name == "Salesforce Einstein Lead Scoring"
        assert restored.results[0].risk_tier == RiskTier.HIGH

    def test_json_enum_as_strings(self):
        """RiskTier and ConfidenceSource serialised as string values."""
        report = _make_report()
        json_str = to_json(report)
        parsed = json.loads(json_str)
        first = parsed["results"][0]
        assert first["risk_tier"] == "HIGH"
        assert first["confidence_source"] == "registry_match"

    def test_json_contains_all_tools(self):
        """JSON contains all tools from the report."""
        report = _make_report()
        json_str = to_json(report)
        parsed = json.loads(json_str)
        assert len(parsed["results"]) == 4


class TestRiskTierDefinitions:
    """Test risk tier definitions in markdown output."""

    def test_markdown_risk_reference_section(self):
        """'## Risk Tier Reference' appears in output."""
        report = _make_report()
        md = to_markdown(report)
        assert "## Risk Tier Reference" in md

    def test_markdown_tier_definition_present(self):
        """For a HIGH result, the plain definition text appears."""
        report = _make_report()
        md = to_markdown(report)
        assert (
            "This AI system makes or significantly influences decisions"
            in md
        )

    def test_markdown_confidence_explanation(self):
        """Confidence line includes explanation for registry match and inferred."""
        report = _make_report()
        md = to_markdown(report)
        assert "found in govai-eu registry" in md
        assert "classified by LLM" in md

    def test_markdown_only_shows_present_tiers(self):
        """Risk Tier Reference only lists tiers present in the report."""
        # Report with only HIGH and MINIMAL
        tools = [
            ClassificationResult(
                tool_name="Tool A",
                risk_tier=RiskTier.HIGH,
                confidence_source=ConfidenceSource.REGISTRY_MATCH,
                raw_input=ToolInput(name="Tool A"),
            ),
            ClassificationResult(
                tool_name="Tool B",
                risk_tier=RiskTier.MINIMAL,
                confidence_source=ConfidenceSource.REGISTRY_MATCH,
                raw_input=ToolInput(name="Tool B"),
            ),
        ]
        report = InventoryReport(
            generated_at=datetime(2026, 3, 23, 12, 0, 0, tzinfo=timezone.utc),
            input_file="test.csv",
            tool_count=2,
            risk_summary={RiskTier.HIGH: 1, RiskTier.MINIMAL: 1},
            results=tools,
        )
        md = to_markdown(report)
        # HIGH and MINIMAL labels should appear
        assert "### HIGH RISK" in md
        assert "### MINIMAL RISK" in md
        # LIMITED and UNCLEAR labels should NOT appear
        assert "### LIMITED RISK" not in md
        assert "### UNCLEAR" not in md


class TestNextSteps:
    """Test next steps section generation."""

    def test_next_steps_high_risk(self):
        """Report with HIGH result mentions Article 9, 11, 14."""
        report = _make_report()  # Has HIGH result
        md = to_markdown(report)
        assert "Article 9" in md
        assert "Article 11" in md
        assert "Article 14" in md

    def test_next_steps_unacceptable(self):
        """Report with UNACCEPTABLE result has discontinue warning."""
        tools = [
            ClassificationResult(
                tool_name="Bad System",
                risk_tier=RiskTier.UNACCEPTABLE,
                confidence_source=ConfidenceSource.REGISTRY_MATCH,
                raw_input=ToolInput(name="Bad System"),
            ),
        ]
        report = InventoryReport(
            generated_at=datetime(2026, 3, 23, 12, 0, 0, tzinfo=timezone.utc),
            input_file="test.csv",
            tool_count=1,
            risk_summary={RiskTier.UNACCEPTABLE: 1},
            results=tools,
        )
        md = to_markdown(report)
        assert "discontinued immediately" in md
        assert "\u26d4" in md

    def test_next_steps_unclear(self):
        """Report with UNCLEAR result says treat as HIGH."""
        report = _make_report()  # Has UNCLEAR result
        md = to_markdown(report)
        assert "Treat each as HIGH RISK" in md

    def test_next_steps_all_clear(self):
        """Report with only MINIMAL results shows all-clear."""
        tools = [
            ClassificationResult(
                tool_name="Safe Tool",
                risk_tier=RiskTier.MINIMAL,
                confidence_source=ConfidenceSource.REGISTRY_MATCH,
                raw_input=ToolInput(name="Safe Tool"),
            ),
        ]
        report = InventoryReport(
            generated_at=datetime(2026, 3, 23, 12, 0, 0, tzinfo=timezone.utc),
            input_file="test.csv",
            tool_count=1,
            risk_summary={RiskTier.MINIMAL: 1},
            results=tools,
        )
        md = to_markdown(report)
        assert "\u2713" in md
        assert "No high-risk AI systems" in md

    def test_next_steps_in_markdown(self):
        """Next steps section appears before Risk Tier Reference in output."""
        report = _make_report()
        md = to_markdown(report)
        next_steps_pos = md.index("Next Steps")
        reference_pos = md.index("## Risk Tier Reference")
        assert next_steps_pos < reference_pos


class TestHtmlReport:
    """Test HTML report generation."""

    def test_html_is_complete_document(self):
        """to_html() output is a complete HTML document."""
        report = _make_report()
        html = to_html(report)
        assert html.strip().startswith("<!DOCTYPE html>")
        assert html.strip().endswith("</html>")

    def test_html_contains_style_block(self):
        """HTML contains a <style> block."""
        report = _make_report()
        html = to_html(report)
        assert "<style>" in html

    def test_html_high_badge_colour(self):
        """HIGH tier badge uses correct colour."""
        report = _make_report()
        html = to_html(report)
        assert "ea580c" in html

    def test_html_minimal_badge_colour(self):
        """MINIMAL tier badge uses correct colour."""
        report = _make_report()
        html = to_html(report)
        assert "16a34a" in html

    def test_html_high_details_open(self):
        """HIGH risk tools use <details open>."""
        report = _make_report()
        html = to_html(report)
        assert "<details open>" in html

    def test_html_minimal_details_closed(self):
        """MINIMAL tools use <details> not <details open>."""
        report = _make_report()
        html = to_html(report)
        # Find the MINIMAL tool's details tag
        minimal_idx = html.index("GitHub Copilot")
        # Search backwards to find the <details> tag
        details_before = html.rfind("<details", 0, minimal_idx)
        tag_end = html.index(">", details_before)
        tag = html[details_before:tag_end + 1]
        assert tag == "<details>"

    def test_html_next_steps_present(self):
        """Next steps content present in HTML output."""
        report = _make_report()
        html = to_html(report)
        assert "next-steps" in html
        assert "Article 11" in html  # HIGH risk present

    def test_html_no_external_deps(self):
        """HTML has no external dependencies."""
        report = _make_report()
        html = to_html(report)
        # No external stylesheets
        assert '<link rel="stylesheet"' not in html
        # No external scripts
        assert "<script src=" not in html
        # No http URLs in the style block
        style_start = html.index("<style>")
        style_end = html.index("</style>")
        style_block = html[style_start:style_end]
        assert "http" not in style_block

    def test_write_reports_html_format(self, tmp_path):
        """write_reports with format='html' creates exactly one .html file."""
        report = _make_report()
        written = write_reports(report, tmp_path, "html")
        assert len(written) == 1
        assert written[0].suffix == ".html"
        assert written[0].exists()

    def test_write_reports_all_format(self, tmp_path):
        """write_reports with format='all' creates .md, .json, and .html."""
        report = _make_report()
        written = write_reports(report, tmp_path, "all")
        suffixes = sorted(p.suffix for p in written)
        assert suffixes == [".html", ".json", ".md"]
        for p in written:
            assert p.exists()
