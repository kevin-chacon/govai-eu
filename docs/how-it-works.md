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

govai-eu does **not** contain the full text of the EU AI Act. Instead, it encodes a simplified version of the regulation's classification framework in four places within the codebase.

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
- **HIGH found:** Lists the 5 specific compliance requirements (technical documentation per Article 11, risk management per Article 9, human oversight per Article 14, audit logging, transparency notices). References the August 2026 enforcement deadline.
- **UNCLEAR found:** Treat-as-HIGH advisory with guidance to contact the vendor.
- **LIMITED found:** Add AI disclosure notices.
- **All MINIMAL:** All-clear message — keep the report as evidence of due diligence.

### 4. The registry entries (`govai/registry/tools/*.yaml`)

Each registry entry contains pre-researched `obligations` and `missing_docs_template` fields that reflect what the EU AI Act requires for that specific tool's risk tier. These were researched by reviewing:

- The tool's vendor documentation and product pages
- The EU AI Act text (particularly Article 6 and Annex III for HIGH risk classification)
- The tool's actual decision-making scope — whether it makes autonomous decisions affecting people's rights

---

## Honest assessment — how well is the EU AI Act reflected?

This section is an honest evaluation of what govai-eu covers, what it doesn't, and when you should use something more sophisticated.

### What govai-eu gets right

**The risk tier model is correct.** The EU AI Act uses a four-tier risk classification (Unacceptable, High, Limited, Minimal). govai-eu implements all four tiers plus UNCLEAR as a safety net. The tier definitions are accurate summaries of the regulation's intent.

**The HIGH risk classification criteria are broadly correct.** The system prompt references Annex III categories (employment, critical infrastructure, education, essential services, law enforcement, migration, justice, democratic processes) and safety components of products under EU product safety law. These are the correct triggers for HIGH risk classification under Articles 6(2) and Annex III.

**The prohibited practices are correct.** The UNACCEPTABLE tier covers the four main prohibited categories from Article 5: social scoring by public authorities, real-time biometric identification in public spaces, subliminal manipulation, and exploitation of vulnerable groups.

**The compliance obligations for HIGH risk are correct.** The next steps section references the right articles: risk management (Article 9), technical documentation (Article 11), and human oversight (Article 14). The enforcement deadline of August 2026 for most high-risk systems is correct.

### What is simplified or missing

**The classification is a simplified summary, not a legal analysis.** The entire EU AI Act is 144 pages with 113 articles, 13 annexes, and hundreds of recitals providing interpretive context. govai-eu distils this into ~6 lines of LLM instruction and 5 dictionary entries. This means:

| EU AI Act element | govai-eu coverage |
|---|---|
| Article 5 — Prohibited practices (8 subcategories) | Covered, but summarised to 4 high-level categories. Misses nuances like the exception for targeted biometric identification in serious crime. |
| Article 6 + Annex III — High-risk classification (8 domains, ~35 specific use cases) | Covered at the domain level. Does not enumerate all 35 specific use cases within each domain. |
| Article 6(1) — Safety components of regulated products | Mentioned in the prompt but not systematically applied. |
| Articles 8–15 — Detailed HIGH risk obligations | Only Articles 9, 11, 14 are referenced. Articles 8 (quality management), 10 (data governance), 12 (record-keeping), 13 (transparency), 15 (accuracy/robustness) are not mentioned. |
| Article 50 — LIMITED risk transparency obligations | Covered generically ("disclose AI") but missing specifics: deepfakes labelling, AI-generated text marking when published on public interest topics. |
| Articles 16–29 — Provider and deployer obligations | Not covered. The regulation distinguishes between providers (who build AI) and deployers (who use it). govai-eu treats the user as a deployer but doesn't explain provider obligations or supply chain duties. |
| Article 53 — GPAI model obligations | Not covered. General-purpose AI model providers (e.g. OpenAI, Anthropic) have separate obligations. govai-eu classifies the end tool, not the underlying model. |
| Annexes IV–XI — Detailed technical standards | Not referenced. These specify the exact content of technical documentation, conformity assessment procedures, and EU database registration. |
| Recitals — Interpretive guidance | Not used. The recitals provide critical context for borderline cases (e.g. when recommendation engines cross from MINIMAL to LIMITED). |
| Delegated acts and implementing acts | Not tracked. The European Commission is expected to issue further specifications that will change the interpretation of several articles. |

**The LLM classification depends on the model's training data.** govai-eu gives the LLM a 6-line classification guide and trusts it to apply this correctly. The quality of the classification depends entirely on:

- How well the LLM understands the tool being classified
- How well the LLM interprets the classification criteria
- Whether the LLM's training data includes the EU AI Act text

Large cloud models (Claude, GPT-4o) generally produce reasonable classifications. Smaller local models may misclassify borderline cases because they have less knowledge of both the tools and the regulation.

**There is no deployer-specific analysis.** The EU AI Act distinguishes between a tool's inherent risk and how an organisation uses it. A CRM system is MINIMAL risk when used for contact management, but could become HIGH risk if an organisation uses its lead scoring to make automated hiring decisions. govai-eu classifies the tool, not the deployment.

**There is no per-tool obligation mapping.** The report says "you need technical documentation" but doesn't generate a checklist of what that documentation must contain (Annex IV specifies 15 items). A compliance professional would need to read the regulation to know what to actually produce.

### When govai-eu is sufficient

- **Initial inventory and awareness.** You want a map of which tools might trigger EU AI Act obligations. govai-eu gives you a starting point that is directionally correct.
- **Internal prioritisation.** Your team needs to know which tools to focus on first. The tier ordering (UNACCEPTABLE → HIGH → LIMITED → MINIMAL) is the right priority.
- **Board-level reporting.** A non-technical summary showing "we have 3 HIGH risk AI systems that need compliance work" is useful and govai-eu produces it well.
- **Due diligence evidence.** Even an imperfect inventory shows you are taking EU AI Act compliance seriously. The report serves as evidence of active risk assessment.

### When you need something more sophisticated

- **You have HIGH risk systems and need to build compliance documentation.** govai-eu tells you that you need a conformity assessment but doesn't tell you how to do one. You need a qualified EU AI Act advisor or a specialised compliance platform.
- **You are a provider (builder) of AI systems, not just a deployer.** Provider obligations (Articles 16–22) are significantly more detailed than deployer obligations. govai-eu doesn't cover them.
- **You need legally defensible classification.** If a regulator asks "why did you classify this as LIMITED?", your answer cannot be "an open-source CLI tool told us so." You need a documented legal analysis tied to specific articles and recitals.
- **You have borderline cases.** When a tool sits between two tiers — for example, a chatbot that also makes automated recommendations affecting access to services — the correct tier depends on a detailed analysis of Articles 6(2), Annex III, and the relevant recitals. govai-eu does not do this analysis.
- **You need to track regulatory changes.** The EU AI Act is supplemented by delegated acts and harmonised standards that are still being drafted. govai-eu does not track these.

### Summary

govai-eu is an **awareness tool, not a compliance tool.** It produces a directionally correct inventory that helps organisations identify which AI tools need attention, in what priority order, and roughly what kind of compliance work is required. Its classification is based on a genuine (if simplified) reading of the EU AI Act.

It should be treated as Step 1 of a compliance process — the step where you find out what you're dealing with. Steps 2 and beyond (detailed legal analysis, documentation production, conformity assessment, monitoring) require human expertise and are outside govai-eu's scope.

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
