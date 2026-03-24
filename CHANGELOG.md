# Changelog

All notable changes to govai-eu will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Planned

- PDF report output
- Document ingestion — extract software lists from invoices, contracts, and procurement documents
- Periodic re-scan with change detection — compare runs over time to detect new tools or tier changes

## [0.1.0] — 2026-03-24

### Added

**CLI commands**

- `govai scan` command — classify a list of software tools under EU AI Act risk tiers from a CSV or plain text file
  - `--llm-model` flag to select any LiteLLM-compatible model (default: `claude-sonnet-4-6`)
  - `--no-llm` flag to skip LLM fallback entirely (unknown tools marked UNCLEAR)
  - `--format` flag with options: `markdown`, `json`, `html`, `both`, `all` (default: `all`)
  - `--output-dir` flag to set report output directory (default: current directory)
- `govai models` command — display a formatted table of 16 supported LLM models across 4 categories (Cloud Proprietary, EU-Based Providers, Other Cloud, Local via Ollama) with provider, API key environment variable, and setup notes

**Registry**

- YAML-based tool registry with 15 pre-classified enterprise AI tools across 4 vendors (Google, HubSpot, Microsoft, Salesforce)
- Schema definition (`registry/schema.yaml`) with 12 fields per tool entry
- Template file (`registry/tools/_template.yaml`) for adding new tools
- Case-insensitive lookup with alias matching

**LLM classification**

- LiteLLM fallback classifier for tools not found in the registry
- Support for Anthropic (Claude), OpenAI (GPT-4o), Google (Gemini), Mistral AI, DeepSeek, Groq, Cohere cloud providers
- Support for local models via Ollama (Llama, Qwen, DeepSeek, Mistral, Phi)
- Structured JSON response parsing with validation
- Graceful error handling — LLM failures return UNCLEAR instead of crashing

**Report output**

- Markdown report with risk summary table, per-tool details grouped by risk tier, and footer disclaimer
- JSON report with Pydantic serialisation for machine-readable integration
- Standalone HTML report with inline CSS, risk tier colour-coded badges, summary cards, collapsible tool sections, and print-friendly `@media print` styles
- Risk tier definitions (`RISK_TIER_DEFINITIONS`) with plain-language explanations, examples, and recommended actions for each tier
- Risk summary table with Meaning column explaining each tier
- Risk Tier Reference section — only includes tiers present in the report
- Next Steps section with severity-based guidance:
  - UNACCEPTABLE: immediate discontinuation warning
  - HIGH: specific EU AI Act articles (9, 11, 14) and compliance requirements
  - UNCLEAR: treat-as-HIGH advisory with vendor contact guidance
  - All-clear message for MINIMAL-only inventories
- Confidence scoring: `registry_match` (found in curated registry) vs `inferred` (classified by LLM) with explanations in report output

**Data models**

- Five EU AI Act risk tiers: UNACCEPTABLE, HIGH, LIMITED, MINIMAL, UNCLEAR
- `ClassificationResult` with tool name, vendor, risk tier, confidence source, AI features, decision scope, data categories, obligations, missing documentation, and notes
- `InventoryReport` with generation timestamp, input file reference, tool count, risk summary, and per-tool results

**Documentation**

- README.md with install instructions, quickstart, model selection guide, input format, risk tier explanations, and limitations
- CONTRIBUTING.md with step-by-step GitHub browser instructions for non-developers
- Registry guide (`docs/registry-guide.md`) with annotated schema, classification decision guide, research tips, common mistakes, and 3 worked YAML examples
- Sample report output (`examples/sample_output.md`)

[Unreleased]: https://github.com/kevin-chacon/govai-eu/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/kevin-chacon/govai-eu/releases/tag/v0.1.0
