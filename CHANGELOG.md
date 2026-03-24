# Changelog

All notable changes to govai-eu will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Planned

- PDF report output
- Document ingestion — extract software lists from invoices, contracts, and procurement documents
- Periodic re-scan with change detection — compare runs over time to detect new tools or tier changes

## [0.2.0] — 2026-03-24

### Changed

- Distribution model: moved from PyPI to GitHub-first install (`git clone` + `pip install -e .`)
- Registry moved inside the `govai` package (`govai/registry/tools/`) so it ships with installs
- README rewritten to focus on community registry contributions
- CONTRIBUTING.md rewritten for non-developer contributors
- `govai models` setup guide updated for GitHub-first workflow

### Added

- `--version` / `-v` flag — outputs `govai-eu <version>` and exits
- Dynamic version from `importlib.metadata` — no hardcoded version string
- API key pre-flight detection — checks if the required env var is set before calling the LLM
- API key warning panel in scan output — yellow box with actionable guidance when key is missing
- `AuthenticationError` handling — specific message for invalid/expired API keys
- API key setup guide in `govai models` — 3 panels: setup, make permanent, Ollama alternative
- API key setup guide in `govai --help` epilog
- `docs/how-it-works.md` — technical overview of how govai-eu works

### Why

The registry is the most valuable part of govai-eu. Growing it requires contributors to be close to the codebase — cloning the repo, seeing the YAML files, and submitting pull requests. PyPI created distance from this workflow. It may return once the registry is mature.

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
- Schema definition (`govai/registry/schema.yaml`) with 12 fields per tool entry
- Template file (`govai/registry/tools/_template.yaml`) for adding new tools
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
- Risk tier definitions with plain-language explanations, examples, and recommended actions
- Next Steps section with severity-based guidance and EU AI Act article references
- Confidence scoring: `registry_match` vs `inferred`

**Data models**

- Five EU AI Act risk tiers: UNACCEPTABLE, HIGH, LIMITED, MINIMAL, UNCLEAR
- `ClassificationResult` with tool name, vendor, risk tier, confidence source, AI features, decision scope, data categories, obligations, missing documentation, and notes
- `InventoryReport` with generation timestamp, input file reference, tool count, risk summary, and per-tool results

**Documentation**

- README.md with install instructions, quickstart, model selection guide, risk tier explanations, and limitations
- CONTRIBUTING.md with step-by-step GitHub browser instructions for non-developers
- Registry guide (`docs/registry-guide.md`) with annotated schema, classification decision guide, and worked examples
- Technical overview (`docs/how-it-works.md`)
- Sample report output (`examples/sample_output.md`)

[Unreleased]: https://github.com/kevin-chacon/govai-eu/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/kevin-chacon/govai-eu/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/kevin-chacon/govai-eu/releases/tag/v0.1.0
