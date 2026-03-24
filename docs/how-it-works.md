# govai-eu — How It Works

A technical overview of what govai-eu does, how the classification pipeline works, what models it supports, and where the EU AI Act information comes from.

---

## What govai-eu is

govai-eu is a Python CLI tool that takes a list of software tools your organisation uses and produces a compliance report classifying each tool under the EU AI Act's risk tiers. It tells you which tools trigger obligations, what those obligations are, and what documentation you probably need to create.

The tool is designed for a non-technical person — a compliance lead, CFO, or operations director — who needs to understand their AI exposure under EU regulation without requiring a data team or system access.

---

## Architecture overview

```
┌─────────────────┐
│   Input file     │   CSV or plain text list of software tools
│ (tools.csv/txt)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Input Parser   │   classifier.py → parse_input_file()
│                  │   Reads CSV (name + optional description)
│                  │   or plain text (one tool per line)
└────────┬────────┘
         │
         ▼
┌─────────────────┐    ┌──────────────────┐
│   Registry       │───▶│  govai/registry/  │  YAML files
│   Lookup         │    │  *.yaml           │  by vendor
│                  │    └──────────────────┘
│  registry.py     │
│  3-pass matching │
└────────┬────────┘
         │ Not found?
         ▼
┌─────────────────┐    ┌──────────────────┐
│   LLM Fallback   │───▶│  LiteLLM         │  Any provider
│                  │    │  (cloud or local) │
│  llm.py          │    └──────────────────┘
│  API key check   │
│  + classification│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Report         │   reporter.py
│   Generation     │   → Markdown (.md)
│                  │   → JSON (.json)
│                  │   → HTML (.html)
└─────────────────┘
```

---

## The classification pipeline

When you run `govai scan tools.csv`, the following happens in order:

### Step 1 — Parse the input file

`classifier.py → parse_input_file()` reads the input file. If it's a CSV, the first column is the tool name and the second column (optional) is a description. If it's any other extension, it's treated as plain text with one tool per line. Comments (lines starting with `#`) and empty lines are skipped.

Each line becomes a `ToolInput(name, description)` object.

### Step 2 — Classify each tool

`classifier.py → classify_tool()` processes each tool through a two-stage pipeline:

**Stage 1: Registry lookup** — The tool name is checked against the built-in YAML registry. The registry is a collection of files in `govai/registry/tools/`, one per vendor (e.g. `microsoft.yaml`, `salesforce.yaml`). Each file contains pre-classified tool entries with risk tier, AI features, obligations, and supporting documentation links.

The lookup uses three passes, in order of priority:

1. **Exact name match** — case-insensitive comparison against the `name` field
2. **Alias match** — case-insensitive comparison against the `aliases` list
3. **Partial match** — checks if the query contains both the vendor name and part of the tool name, or if the tool name contains the query

If a match is found, the result is returned with confidence `registry_match`. No LLM call is made.

**Stage 2: LLM fallback** — If the tool is not found in the registry:

- If `--no-llm` was passed: the tool is marked `UNCLEAR` with the note "Not in registry; LLM fallback disabled"
- Otherwise: the tool is sent to the LLM for classification via `llm.py → classify_with_llm()`

Before calling the LLM, a pre-flight check verifies that the required API key environment variable is set (using `MODEL_KEY_MAP`). If the key is missing, the tool is marked `UNCLEAR` with an actionable error message — no LLM call is made.

If the key is present, `litellm.completion()` is called with a structured system prompt that instructs the model to return a JSON object containing the risk tier, AI features, decision scope, data categories, obligations, and missing documentation.

Results from the LLM are returned with confidence `inferred`.

### Step 3 — Build the report

`classifier.py → classify_inventory()` collects all results, builds a risk summary (count of tools per tier), and returns an `InventoryReport` object.

### Step 4 — Generate output files

`reporter.py → write_reports()` generates the requested output formats:

- **Markdown** — risk summary table, tool-by-tool details grouped and ordered by risk tier (UNACCEPTABLE → HIGH → LIMITED → MINIMAL → UNCLEAR), a next steps section with specific EU AI Act article references, a risk tier reference section, and a disclaimer
- **JSON** — Pydantic-serialised report with enums as strings, suitable for integration with other systems
- **HTML** — standalone file with inline CSS, colour-coded risk tier badges, summary cards, collapsible `<details>` sections for each tool, and `@media print` styles for clean printing. No external dependencies — opens offline in any browser.

---

## The data models

Defined in `govai/models.py`:

| Model | Purpose |
|---|---|
| `RiskTier` | Enum: UNACCEPTABLE, HIGH, LIMITED, MINIMAL, UNCLEAR |
| `ConfidenceSource` | Enum: `registry_match` (from curated YAML) or `inferred` (from LLM) |
| `ToolInput` | What the user provides: name + optional description |
| `ClassificationResult` | Full classification: tool name, vendor, risk tier, confidence source, AI features, decision scope, data categories, obligations, missing docs, notes |
| `InventoryReport` | Container: timestamp, input file, tool count, risk summary dict, list of ClassificationResults |

---

## The registry

The registry is the most accurate part of govai. It contains hand-curated YAML entries that have been researched against vendor documentation, with a `source_url` and `last_verified` date for each entry.

**Current coverage:** 15 tool entries across 4 vendor files (Google, HubSpot, Microsoft, Salesforce).

Each entry follows the schema defined in `registry/schema.yaml`:

```yaml
- name: "Salesforce Einstein Lead Scoring"
  vendor: "Salesforce"
  aliases: ["Einstein Lead Scoring", "SFDC Einstein"]
  risk_tier: "HIGH"
  ai_features: ["Predictive lead scoring", "Automated lead routing"]
  decision_scope: "Scores and ranks leads automatically"
  data_categories: ["Lead contact data", "Sales pipeline data"]
  obligations: ["Conformity assessment", "Risk management system"]
  missing_docs_template: ["Conformity assessment report", "Bias audit results"]
  source_url: "https://help.salesforce.com/..."
  last_verified: "2026-03"
  notes: null
```

The `RegistryLoader` class loads all YAML files at module import time into a singleton. The `lookup()` function provides the public API.

---

## Supported LLM models

govai uses [LiteLLM](https://docs.litellm.ai/docs/providers) as a universal adapter, which means it works with any LiteLLM-supported model. The following are explicitly tested and documented:

| Category | Models | Provider | API Key Env Var |
|---|---|---|---|
| **Cloud — Proprietary** | `claude-sonnet-4-6` (default), `claude-opus-4-6` | Anthropic | `ANTHROPIC_API_KEY` |
| | `gpt-4o`, `gpt-4o-mini` | OpenAI | `OPENAI_API_KEY` |
| | `gemini/gemini-2.0-flash` | Google | `GEMINI_API_KEY` |
| **EU-Based** | `mistral/mistral-large-latest`, `mistral/mistral-small-latest` | Mistral AI | `MISTRAL_API_KEY` |
| **Other Cloud** | `deepseek/deepseek-chat` | DeepSeek | `DEEPSEEK_API_KEY` |
| | `groq/llama-3.3-70b-versatile` | Groq | `GROQ_API_KEY` |
| | `cohere/command-r-plus` | Cohere | `COHERE_API_KEY` |
| **Local (Ollama)** | `ollama/llama3.2`, `ollama/qwen2.5`, `ollama/qwen3`, `ollama/deepseek-r1`, `ollama/mistral`, `ollama/phi4` | Ollama | None |

Local models via Ollama require no API key and send no data outside the machine. Cloud models generally produce more accurate classifications.

The `MODEL_KEY_MAP` in `llm.py` maps model string prefixes to their required environment variable, enabling the pre-flight API key check.

---

## How EU AI Act information is used

govai-eu does **not** contain the full text of the EU AI Act. Instead, it encodes the regulation's classification framework in three places:

### 1. The LLM system prompt (`llm.py`)

The system prompt given to the LLM contains a condensed classification guide:

- **UNACCEPTABLE:** Social scoring by public authorities, real-time biometric surveillance in public spaces, manipulation of vulnerable groups, subliminal behavioural manipulation.
- **HIGH:** Annex III systems — critical infrastructure, education, employment/HR decisions (hiring, promotion, termination), access to essential services, law enforcement, migration, administration of justice, democratic processes. Also: safety components of products covered by EU product safety law.
- **LIMITED:** Transparency obligations — chatbots (must disclose AI), emotion recognition, AI-generated or manipulated content.
- **MINIMAL:** All other AI — general assistants, search, spam filters, recommendation engines in most contexts, productivity AI.
- **UNCLEAR:** Risk depends on deployment configuration and cannot be determined from available information.

This is a distillation of the EU AI Act's risk classification framework (primarily Articles 5, 6, and Annex III) into decision rules the LLM can apply. The prompt also instructs the model not to over-classify and to use UNCLEAR when risk genuinely depends on configuration.

### 2. Risk tier definitions (`reporter.py`)

The `RISK_TIER_DEFINITIONS` dictionary contains plain-language explanations for each tier that appear in the generated reports. Each entry includes:

- A human-readable label (e.g. "HIGH RISK")
- A plain-language explanation of what the tier means
- Real-world examples of tools that fall into this tier
- A recommended action, referencing specific EU AI Act articles where applicable (e.g. Article 9 for risk management, Article 11 for technical documentation, Article 14 for human oversight)

These definitions are shown in the report's "Risk Tier Reference" section so readers can understand what each tier means without looking up the regulation.

### 3. The next steps section (`reporter.py`)

The `next_steps_section()` function generates severity-based guidance depending on which tiers appear in the report:

- **UNACCEPTABLE found:** Immediate discontinuation warning. No grace period.
- **HIGH found:** Lists the 5 specific compliance requirements (technical documentation per Article 11, risk management per Article 9, human oversight per Article 14, audit logging, transparency notices).
- **UNCLEAR found:** Treat-as-HIGH advisory with guidance to contact the vendor.
- **LIMITED found:** Add AI disclosure notices.
- **All MINIMAL:** All-clear message — keep the report as evidence of due diligence.

### 4. The registry entries (`govai/registry/tools/*.yaml`)

Each registry entry contains pre-researched `obligations` and `missing_docs_template` fields that reflect what the EU AI Act requires for that specific tool's risk tier. These were researched by reviewing:

- The tool's vendor documentation and product pages
- The EU AI Act text (particularly Article 6 and Annex III for HIGH risk classification)
- The tool's actual decision-making scope — whether it makes autonomous decisions affecting people's rights

### What govai-eu does NOT do

- It does not claim to be a legal interpretation of the EU AI Act
- It does not have access to the full regulatory text at runtime
- It does not track regulatory changes automatically
- It does not replace qualified legal advice

The classification framework is based on the published EU AI Act text as of 2026. Registry entries are versioned with a `last_verified` date so users can see when each classification was last checked.

---

## File structure

```
govai/
  __init__.py       Version string (from importlib.metadata)
  models.py         Pydantic data models
  registry.py       YAML loader + 3-pass lookup
  llm.py            LiteLLM fallback classifier
  classifier.py     Orchestration: parse input → classify → build report
  reporter.py       Markdown, JSON, and HTML report generation
  cli.py            Typer CLI: scan, models, --version

registry/
  schema.yaml       Field definitions for tool entries
  tools/
    _template.yaml  Empty template for new entries
    google.yaml     Google Cloud AI tools
    hubspot.yaml    HubSpot AI tools
    microsoft.yaml  Microsoft AI tools (M365, Azure, Dynamics)
    salesforce.yaml Salesforce AI tools (Einstein suite)

tests/
  test_models.py    Data model serialisation and validation
  test_registry.py  Registry lookup: exact, alias, case-insensitive
  test_classifier.py Pipeline: registry hit, LLM fallback, input parsing
  test_reporter.py  Report generation: markdown, JSON, HTML, next steps
  test_cli.py       CLI commands: scan, models, --version
  test_llm.py       API key detection and Ollama bypass
```

---

## Test coverage

79 tests across 6 test files. All tests run without external API keys or network access — LLM calls are mocked.

```
pytest tests/ -q
79 passed
```
