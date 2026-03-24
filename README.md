# govai-eu

EU AI Act compliance inventory from a plain software list.

## What it does

You give govai a list of AI tools your organisation uses. It classifies each one by EU AI Act risk tier — UNACCEPTABLE, HIGH, LIMITED, MINIMAL, or UNCLEAR. It tells you what documentation is required and what is probably missing. It works offline with local models or with any cloud LLM.

## Quick start

```bash
git clone https://github.com/kevin-chacon/govai-eu.git
cd govai-eu
pip install -e .
govai scan your_tools.csv
```

That's the entire install. No account needed. No API key needed if you use a local model.

Your input file is a CSV or plain text file with one tool per line:

```text
Salesforce Einstein, sales lead scoring
Microsoft 365 Copilot
HubSpot ChatSpot
GitHub Copilot
```

govai produces three report files by default — Markdown, JSON, and a standalone HTML report designed for sharing with legal or compliance teams.

## Setting up an LLM

govai checks its built-in registry first — no LLM needed for known tools. For tools not in the registry, it falls back to an LLM for classification. You have two options:

**Option A — Local model (no data leaves your machine):**

```bash
# Install Ollama from ollama.com, then:
ollama pull llama3.2
govai scan tools.csv --llm-model ollama/llama3.2
```

No account, no API key, completely free.

**Option B — Cloud model (more accurate, requires API key):**

```bash
export ANTHROPIC_API_KEY="your-key"          # Mac/Linux
set ANTHROPIC_API_KEY=your-key               # Windows CMD
$env:ANTHROPIC_API_KEY="your-key"            # Windows PowerShell

govai scan tools.csv --llm-model claude-sonnet-4-20250514
```

Run `govai models` to see all supported providers with setup instructions.

**Skip the LLM entirely:**

```bash
govai scan tools.csv --no-llm
```

Tools not found in the registry will be marked UNCLEAR.

## The registry — why it matters

The registry is a collection of YAML files in `govai/registry/tools/`. Each file describes one vendor's AI tools and their EU AI Act risk classifications. When someone runs `govai scan`, the registry is checked first. If a tool is in the registry, it gets an instant, human-verified classification — no LLM needed.

**The registry currently contains 15 pre-classified enterprise AI tools across 4 vendors.**

The registry is what makes govai-eu accurate and useful. The more tools it contains, the better it works for everyone. Every tool you add saves the next user from relying on an LLM guess.

**You don't need to be a developer to contribute.** If you know what an AI tool does and how it's used, you can add it to the registry. See [CONTRIBUTING.md](CONTRIBUTING.md) for step-by-step instructions.

## Understanding the report

govai classifies each tool into one of five EU AI Act risk tiers:

| Tier | What it means |
|---|---|
| **UNACCEPTABLE** | Prohibited under the EU AI Act — must be discontinued. |
| **HIGH** | Makes decisions affecting people's rights, employment, or access to services — strict compliance obligations apply. |
| **LIMITED** | Users must be told they are interacting with AI — transparency obligations apply. |
| **MINIMAL** | No specific EU AI Act obligations beyond general good practice. |
| **UNCLEAR** | Risk tier could not be determined — treat as HIGH until verified. |

Each report includes a **Next Steps** section that tells you exactly what to do based on the risk tiers found, referencing specific EU AI Act articles where relevant.

## Output formats

```bash
govai scan tools.csv                    # markdown + JSON + HTML (default)
govai scan tools.csv --format markdown  # markdown only
govai scan tools.csv --format json      # JSON only
govai scan tools.csv --format html      # HTML only
govai scan tools.csv --format both      # markdown + JSON
```

The HTML report is a single standalone file with no external dependencies. It opens offline in any browser and prints cleanly. It is designed for sharing with legal or compliance teams who may not use the command line.

## What govai-eu does NOT do

- **Not a legal opinion.** govai-eu is a starting point for EU AI Act compliance review, not a substitute for qualified legal advice.
- **Cannot detect tools not on the input list.** If a tool is not in your input file, it will not appear in the report. Shadow AI — tools used by employees without formal approval — cannot be discovered by govai-eu.
- **Inferred classifications should be verified.** Any classification marked `inferred` was produced by an LLM and should be reviewed by a human before being relied upon.
- **Smaller local models may misclassify edge cases.** Local models via Ollama are private and free, but may produce less accurate classifications than large cloud models. If accuracy matters more than privacy for your use case, use a cloud model.

## Contributing

The most useful thing anyone can do is add a tool to the registry. No coding required — you fill in a YAML template, submit a pull request, and a maintainer reviews it. See [CONTRIBUTING.md](CONTRIBUTING.md) for step-by-step instructions written for non-developers.

## License

MIT

## Links

- **Repository:** [github.com/kevin-chacon/govai-eu](https://github.com/kevin-chacon/govai-eu)
- **Issues:** [github.com/kevin-chacon/govai-eu/issues](https://github.com/kevin-chacon/govai-eu/issues)
