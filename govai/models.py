"""Pydantic v2 data models for govai."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RiskTier(str, Enum):
    """EU AI Act risk tiers."""

    UNACCEPTABLE = "UNACCEPTABLE"
    HIGH = "HIGH"
    LIMITED = "LIMITED"
    MINIMAL = "MINIMAL"
    UNCLEAR = "UNCLEAR"


class ConfidenceSource(str, Enum):
    """How the classification was determined."""

    REGISTRY_MATCH = "registry_match"
    INFERRED = "inferred"


class ToolInput(BaseModel):
    """A tool to be classified."""

    name: str
    description: Optional[str] = None


class ClassificationResult(BaseModel):
    """Classification of a single tool under the EU AI Act."""

    tool_name: str
    vendor: Optional[str] = None
    risk_tier: RiskTier
    confidence_source: ConfidenceSource
    ai_features: list[str] = Field(default_factory=list)
    decision_scope: Optional[str] = None
    data_categories: list[str] = Field(default_factory=list)
    obligations: list[str] = Field(default_factory=list)
    missing_docs: list[str] = Field(default_factory=list)
    notes: Optional[str] = None
    raw_input: ToolInput


class InventoryReport(BaseModel):
    """Complete inventory report covering all classified tools."""

    generated_at: datetime
    input_file: str
    tool_count: int
    risk_summary: dict[RiskTier, int]
    results: list[ClassificationResult]
