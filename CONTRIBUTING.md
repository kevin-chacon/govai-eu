# Contributing to govai-eu

The registry is the most valuable part of govai-eu. The most useful thing anyone can do is add a tool they know about that isn't in the registry yet. You don't need to write code — just fill in a YAML template and submit a pull request.

## How to add a tool — step by step

You can do this entirely in your web browser. No software to install.

### Step 1 — Go to the registry

Go to [github.com/kevin-chacon/govai-eu](https://github.com/kevin-chacon/govai-eu) and navigate to the `govai/registry/tools/` folder.

### Step 2 — Check if the vendor already has a file

Look at the existing files. They are named by vendor — for example, `microsoft.yaml` contains all Microsoft tools. If your tool's vendor already has a file, you'll add your tool to that file. If not, you'll create a new file.

### Step 3 — Edit or create the file

- **If the vendor file exists:** Click on it, then click the pencil icon (✏️) to edit.
- **If the vendor file does not exist:** Click "Add file" → "Create new file". Name it `your-vendor.yaml` (all lowercase, e.g. `personio.yaml`).

### Step 4 — Copy the template

Copy the structure from [`govai/registry/tools/_template.yaml`](https://github.com/kevin-chacon/govai-eu/blob/main/govai/registry/tools/_template.yaml). If you're adding to an existing file, paste it at the bottom.

### Step 5 — Fill in each field

| Field | What to put here |
|---|---|
| `name` | The full product name as people normally refer to it. Example: `"Salesforce Einstein Lead Scoring"` |
| `vendor` | The company that makes the tool. Example: `"Salesforce"` |
| `aliases` | Other names people use for this tool — abbreviations, short names. Example: `["Einstein Lead Scoring", "SFDC Einstein"]` |
| `risk_tier` | The EU AI Act risk tier. One of: `UNACCEPTABLE`, `HIGH`, `LIMITED`, `MINIMAL`, `UNCLEAR`. See the classification guide below. |
| `ai_features` | Specific AI capabilities the tool provides. Example: `["Predictive lead scoring", "Automated lead routing"]` |
| `decision_scope` | What autonomous decisions the tool makes. If it only suggests and a human decides, say so. If none, use `null`. |
| `data_categories` | Types of data the AI processes. Example: `["Lead contact data", "Sales pipeline data"]` |
| `obligations` | EU AI Act requirements for this risk tier. Example: `["Conformity assessment", "Risk management system"]` |
| `missing_docs_template` | Documentation typically absent. Example: `["Conformity assessment report", "Bias audit results"]` |
| `source_url` | URL to vendor documentation where you found this information. Must be a real, working link. |
| `last_verified` | The month you checked this information, in `YYYY-MM` format. Example: `"2026-03"` |
| `notes` | Optional. Caveats about when the risk tier might differ. Use `null` if none. |

### Step 6 — Submit your change

1. Scroll to the bottom and click **"Propose changes"**
2. On the next page, click **"Create pull request"**
3. Add a title like: `registry: add Personio HR`
4. Click **"Create pull request"** to submit

A maintainer will review your entry and merge it.

## How to classify a tool correctly

The key question:

> **Does this tool make autonomous decisions that affect a person's rights, employment, or access to services?**

- **If yes → HIGH.** Examples: a tool that automatically screens CVs, scores credit applications, or routes customer complaints without human review.
- **If the tool interacts directly with users and they should know it's AI → LIMITED.** Examples: chatbots, AI-generated content tools.
- **If the tool assists a human who makes the final decision → probably MINIMAL.** Examples: a writing assistant, a code completion tool, a spam filter.
- **If the risk depends on how the tool is configured → UNCLEAR.** Explain in the notes field what information would resolve it.

### Common mistakes

- **Don't classify everything as HIGH.** A writing assistant is not HIGH just because it "uses AI". It becomes HIGH only if it makes autonomous decisions affecting people's rights.
- **Don't confuse "uses AI" with "makes autonomous decisions."** A search engine uses AI but doesn't make decisions about people's employment.
- **When genuinely unsure, use UNCLEAR and explain why.** Over-classifying creates noise and undermines trust.

## What makes a good contribution

- **Accurate classification with a source URL** — not a blog post, but the vendor's product documentation
- **One tool per pull request** — easier to review
- **Risk tier matches the tool's actual decision-making scope** — not just its category
- **Notes field explains any configuration-dependent factors**
- **`last_verified` set to the current month**

## For developers

If you want to contribute code:

```bash
git clone https://github.com/kevin-chacon/govai-eu.git
cd govai-eu
pip install -e ".[dev]"
pytest
ruff check govai/
```

Open an issue before writing code so we can discuss the approach first.

## Code of conduct

Respectful, evidence-based disagreements about classifications are welcome. Personal attacks and bad-faith arguments are not acceptable.
