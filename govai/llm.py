"""LLM fallback classifier using LiteLLM."""

from __future__ import annotations

import json
import re

import litellm

from govai.models import (
    ClassificationResult,
    ConfidenceSource,
    RiskTier,
    ToolInput,
)

# Suppress LiteLLM debug output
litellm.suppress_debug_info = True
litellm.set_verbose = False

DEFAULT_MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are an EU AI Act classification expert. Classify the given software tool under the EU AI Act risk tiers.

Risk tier definitions:

UNACCEPTABLE: Prohibited. Social scoring by public authorities, real-time biometric surveillance in public spaces, manipulation of vulnerable groups, subliminal behavioural manipulation.

HIGH: Annex III systems — critical infrastructure, education, employment/HR decisions (hiring, promotion, termination), access to essential services, law enforcement, migration, administration of justice, democratic processes. Also: safety components of products covered by EU product safety law.

LIMITED: Transparency obligations. Chatbots (must disclose AI), emotion recognition, AI-generated or manipulated content.

MINIMAL: All other AI. General assistants, search, spam filters, recommendation engines in most contexts, productivity AI.

UNCLEAR: Risk depends on deployment configuration and cannot be determined from available information.

Rules:
- Return ONLY valid JSON. No markdown, no preamble, no explanation.
- Do NOT over-classify — accuracy matters more than caution.
- Use UNCLEAR when risk genuinely depends on configuration.

Return this exact JSON schema:
{
  "risk_tier": "HIGH",
  "ai_features": ["list of specific AI capabilities"],
  "decision_scope": "description of autonomous decisions, or null",
  "data_categories": ["types of data the AI processes"],
  "obligations": ["specific EU AI Act obligations"],
  "missing_docs": ["documentation typically absent"],
  "notes": "caveats or null",
  "vendor": "company name or null"
}"""


def classify_with_llm(
    tool: ToolInput, model: str = DEFAULT_MODEL
) -> ClassificationResult:
    """Classify a tool using LiteLLM. Never raises — returns UNCLEAR on failure."""
    try:
        user_prompt = _build_user_prompt(tool)
        response = litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=1000,
        )
        raw = response.choices[0].message.content
        return _parse_response(raw, tool)
    except Exception as exc:
        return _unclear_result(tool, f"LLM classification failed: {exc}")


def _build_user_prompt(tool: ToolInput) -> str:
    """Build the user message for the LLM."""
    prompt = f"Classify this software tool under the EU AI Act:\n\nTool name: {tool.name}"
    if tool.description:
        prompt += f"\nDescription: {tool.description}"
    return prompt


def _parse_response(raw: str, tool: ToolInput) -> ClassificationResult:
    """Parse the LLM JSON response into a ClassificationResult."""
    # Strip markdown code fences if present
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", raw.strip())
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        return _unclear_result(tool, f"Failed to parse LLM response as JSON: {exc}")

    # Validate risk_tier
    risk_str = data.get("risk_tier", "UNCLEAR").upper()
    try:
        risk_tier = RiskTier(risk_str)
    except ValueError:
        risk_tier = RiskTier.UNCLEAR

    return ClassificationResult(
        tool_name=tool.name,
        vendor=data.get("vendor"),
        risk_tier=risk_tier,
        confidence_source=ConfidenceSource.INFERRED,
        ai_features=data.get("ai_features", []) or [],
        decision_scope=data.get("decision_scope"),
        data_categories=data.get("data_categories", []) or [],
        obligations=data.get("obligations", []) or [],
        missing_docs=data.get("missing_docs", []) or [],
        notes=data.get("notes"),
        raw_input=tool,
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
