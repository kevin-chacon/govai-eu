"""Classifier orchestration: registry lookup + LLM fallback."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console as RichConsole
from rich.progress import Progress

from govai.models import (
    ClassificationResult,
    ConfidenceSource,
    InventoryReport,
    RiskTier,
    ToolInput,
)
from govai import llm, registry


def classify_tool(
    tool: ToolInput, model: str, no_llm: bool
) -> ClassificationResult:
    """Classify a single tool: registry first, then LLM fallback.

    1. Try registry lookup
    2. If found: return registry result
    3. If not found and no_llm=True: return UNCLEAR
    4. If not found and no_llm=False: return LLM classification
    """
    result = registry.lookup(tool.name)
    if result is not None:
        # Preserve the original raw_input with description if present
        result.raw_input = tool
        return result

    if no_llm:
        return _unclear_result(tool, "Not in registry; LLM fallback disabled")

    return llm.classify_with_llm(tool, model)


def parse_input_file(path: Path) -> list[ToolInput]:
    """Parse a CSV or plain text file into a list of ToolInput.

    - CSV (.csv): first column = name, second column = description (optional)
    - Plain text (any other extension): one tool per line, no description
    - Skip empty lines and lines starting with # (comments)
    - Strip whitespace from all values
    """
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    text = path.read_text(encoding="utf-8")
    tools: list[ToolInput] = []

    if path.suffix.lower() == ".csv":
        reader = csv.reader(text.splitlines())
        for row in reader:
            if not row:
                continue
            name = row[0].strip()
            if not name or name.startswith("#"):
                continue
            # Skip header row
            if name.lower() == "tool_name":
                continue
            description = row[1].strip() if len(row) > 1 and row[1].strip() else None
            tools.append(ToolInput(name=name, description=description))
    else:
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            tools.append(ToolInput(name=stripped))

    return tools


def classify_inventory(
    tools: list[ToolInput],
    model: str,
    no_llm: bool,
    input_file: str = "unknown",
) -> InventoryReport:
    """Classify all tools and build an InventoryReport.

    Shows a progress bar on stderr using rich.progress.
    """
    results: list[ClassificationResult] = []

    stderr_console = RichConsole(stderr=True)
    with Progress(transient=True, console=stderr_console) as progress:
        task = progress.add_task("Classifying tools...", total=len(tools))
        for tool in tools:
            result = classify_tool(tool, model, no_llm)
            results.append(result)
            progress.advance(task)

    # Build risk summary
    risk_summary: dict[RiskTier, int] = {}
    for tier in RiskTier:
        count = sum(1 for r in results if r.risk_tier == tier)
        if count > 0:
            risk_summary[tier] = count

    return InventoryReport(
        generated_at=datetime.now(timezone.utc),
        input_file=input_file,
        tool_count=len(results),
        risk_summary=risk_summary,
        results=results,
    )


def _unclear_result(tool: ToolInput, notes: str) -> ClassificationResult:
    """Return an UNCLEAR result with explanatory notes."""
    return ClassificationResult(
        tool_name=tool.name,
        risk_tier=RiskTier.UNCLEAR,
        confidence_source=ConfidenceSource.INFERRED,
        notes=notes,
        raw_input=tool,
    )
