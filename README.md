# govai-eu

govai-eu inventories the AI systems your organisation uses and classifies them under EU AI Act risk tiers — from a plain software list.

## Why this exists

Most companies don't know which of their software tools contain AI features, let alone which EU AI Act obligations those features trigger. High-risk enforcement begins **August 2026**. govai-eu produces a structured compliance inventory report from a simple list of tools — no data team, no system access, and no technical knowledge required.

## Install

```bash
pip install govai-eu
pip install govai-eu[anthropic]   # for Claude (default model)
pip install govai-eu[openai]      # for GPT-4o
# Ollama (local models) needs no extra package
```

> **Note:** The PyPI package is `govai-eu`. The CLI command it installs is `govai`.
> You run `govai scan`, not `govai-eu scan`.

## Quickstart

Create a file listing the software tools your organisation uses:

```text
Salesforce Einstein, sales lead scoring
Microsoft 365 Copilot
HubSpot ChatSpot
GitHub Copilot
Workday HCM
```

Run govai:

```bash
govai scan tools.txt
```

govai produces three report files in the current directory:

- **`govai_report_<timestamp>.md`** — Markdown report with risk summary, next steps, tier reference, and per-tool details
- **`govai_report_<timestamp>.json`** — Machine-readable JSON for integration with other systems
- **`govai_report_<timestamp>.html`** — Standalone HTML file with risk tier badges, collapsible tool sections, and print-friendly styling — designed for sharing with legal or compliance teams

Each report includes a plain-language **Next Steps** section that tells you exactly what to do based on the risk tiers found, referencing specific EU AI Act articles where relevant.

## Choosing your LLM model

Tools not found in the built-in registry are classified by an LLM via [LiteLLM](https://docs.litellm.ai/docs/providers). You can choose any LiteLLM-compatible model with the `--llm-model` flag. The default is `claude-sonnet-4-6`.

Run `govai models` in your terminal to see all supported options with setup instructions.

| Model string | Provider | API key env var | Notes |
|---|---|---|---|
| `claude-sonnet-4-6` | Anthropic | `ANTHROPIC_API_KEY` | Default. Best accuracy. |
| `gpt-4o` | OpenAI | `OPENAI_API_KEY` | Strong alternative. |
| `mistral/mistral-large-latest` | Mistral AI | `MISTRAL_API_KEY` | French company, EU data residency. |
| `deepseek/deepseek-chat` | DeepSeek | `DEEPSEEK_API_KEY` | Strong reasoning, very low cost. |
| `ollama/llama3.2` | Ollama | None (local) | No data leaves your machine. |

```bash
# Use GPT-4o instead of the default
govai scan tools.txt --llm-model gpt-4o

# Use a local Ollama model (no API key, no data leaves your machine)
govai scan tools.txt --llm-model ollama/llama3.2

# Skip LLM entirely — unknown tools marked UNCLEAR
govai scan tools.txt --no-llm
```

## Input format

**CSV** (`.csv` extension) — tool name in the first column, optional description in the second:

```csv
Salesforce Einstein,Lead scoring and opportunity insights
Microsoft 365 Copilot,AI assistant in Office apps
HubSpot ChatSpot,Conversational AI for CRM
```

**Plain text** (any other extension) — one tool per line:

```text
Salesforce Einstein
Microsoft 365 Copilot
HubSpot ChatSpot
```

Lines starting with `#` are treated as comments and skipped. Empty lines are ignored.

## Understanding the report

govai classifies each tool into one of five EU AI Act risk tiers:

| Tier | What it means |
|---|---|
| **UNACCEPTABLE** | Prohibited under the EU AI Act. Must be discontinued. |
| **HIGH** | Makes or influences decisions affecting people's rights, employment, or access to services. Strict compliance obligations apply. |
| **LIMITED** | Has transparency obligations — users must be told they are interacting with AI. |
| **MINIMAL** | No specific EU AI Act obligations beyond general good practice. |
| **UNCLEAR** | Risk tier could not be determined. Depends on how the tool is configured or deployed. Treat as HIGH until verified. |

## Output formats

```bash
govai scan tools.csv                  # markdown + JSON + HTML (default)
govai scan tools.csv --format markdown    # markdown only
govai scan tools.csv --format json        # JSON only
govai scan tools.csv --format html        # HTML only
govai scan tools.csv --format both        # markdown + JSON
```

The HTML report is a single standalone file with no external dependencies. It opens offline in any browser and prints cleanly. It is designed for sharing with legal or compliance teams who may not use the command line.

## What govai-eu does NOT do

- **Not a legal opinion.** govai-eu is a starting point for EU AI Act compliance review, not a substitute for qualified legal advice.
- **Cannot detect tools not on the input list.** If a tool is not in your input file, it will not appear in the report.
- **Shadow AI will not appear.** AI tools used by employees that are not on the submitted list have no way to be discovered by govai-eu.
- **Inferred classifications should be verified.** Any classification marked `inferred` was produced by an LLM and should be reviewed by a human.
- **Local models sacrifice accuracy for privacy.** Smaller local models via Ollama may produce less accurate classifications than large cloud models.

## Contributing

The most valuable contribution anyone can make is **adding tools to the registry**. The registry ships with 15 pre-classified enterprise AI tools across 4 vendors. Every tool you add saves the next user from needing an LLM classification for that tool.

See [CONTRIBUTING.md](CONTRIBUTING.md) for step-by-step instructions. No coding experience required — the primary contribution path is adding YAML entries.

## License

MIT

## Links

- **Repository:** [github.com/kevin-chacon/govai-eu](https://github.com/kevin-chacon/govai-eu)
- **Issues:** [github.com/kevin-chacon/govai-eu/issues](https://github.com/kevin-chacon/govai-eu/issues)
- **PyPI:** `pip install govai-eu`
