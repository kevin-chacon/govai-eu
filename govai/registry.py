"""Registry loader: loads YAML tool definitions and provides lookup."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml

from govai.models import (
    ClassificationResult,
    ConfidenceSource,
    RiskTier,
    ToolInput,
)

# Default registry path: registry/tools/ relative to project root
_REGISTRY_DIR = Path(__file__).resolve().parent.parent / "registry" / "tools"


class RegistryLoader:
    """Loads YAML registry files and provides case-insensitive tool lookup."""

    def __init__(self, registry_dir: Path | None = None) -> None:
        self._entries: list[dict] = []
        self._dir = registry_dir or _REGISTRY_DIR
        self._load_all()

    def _load_all(self) -> None:
        """Load all .yaml files from the registry directory recursively."""
        if not self._dir.exists():
            return

        for yaml_path in sorted(self._dir.rglob("*.yaml")):
            # Skip template file
            if yaml_path.name.startswith("_"):
                continue

            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                raise ValueError(
                    f"Failed to parse YAML file: {yaml_path.name}"
                ) from exc

            if data is None:
                continue

            # Each file contains a list of tool entries
            if isinstance(data, list):
                for entry in data:
                    if isinstance(entry, dict):
                        self._entries.append(entry)
            elif isinstance(data, dict):
                self._entries.append(data)

    def lookup(self, tool_name: str) -> Optional[ClassificationResult]:
        """Look up a tool by name, alias, or partial vendor+name match.

        Match priority: exact name → aliases → partial vendor+name.
        All matching is case-insensitive with stripped whitespace.
        """
        query = tool_name.strip().lower()
        if not query:
            return None

        # Pass 1: exact name match
        for entry in self._entries:
            if entry.get("name", "").strip().lower() == query:
                return self._entry_to_result(entry, tool_name)

        # Pass 2: alias match
        for entry in self._entries:
            aliases = entry.get("aliases", []) or []
            for alias in aliases:
                if alias.strip().lower() == query:
                    return self._entry_to_result(entry, tool_name)

        # Pass 3: partial vendor+name match
        for entry in self._entries:
            name_lower = entry.get("name", "").strip().lower()
            vendor = entry.get("vendor", "")
            vendor_lower = vendor.strip().lower() if vendor else ""
            # Check if query contains both vendor and part of name
            if vendor_lower and vendor_lower in query and name_lower in query:
                return self._entry_to_result(entry, tool_name)
            # Check if entry name contains the query
            if query in name_lower:
                return self._entry_to_result(entry, tool_name)

        return None

    @staticmethod
    def _entry_to_result(
        entry: dict, original_name: str
    ) -> ClassificationResult:
        """Convert a YAML entry dict into a ClassificationResult."""
        risk_str = entry.get("risk_tier", "UNCLEAR").upper()
        try:
            risk_tier = RiskTier(risk_str)
        except ValueError:
            risk_tier = RiskTier.UNCLEAR

        return ClassificationResult(
            tool_name=entry.get("name", original_name),
            vendor=entry.get("vendor"),
            risk_tier=risk_tier,
            confidence_source=ConfidenceSource.REGISTRY_MATCH,
            ai_features=entry.get("ai_features", []) or [],
            decision_scope=entry.get("decision_scope"),
            data_categories=entry.get("data_categories", []) or [],
            obligations=entry.get("obligations", []) or [],
            missing_docs=entry.get("missing_docs_template", []) or [],
            notes=entry.get("notes"),
            raw_input=ToolInput(name=original_name),
        )


# Module-level singleton
_registry = RegistryLoader()


def lookup(tool_name: str) -> Optional[ClassificationResult]:
    """Public lookup function using the module-level singleton."""
    return _registry.lookup(tool_name)
