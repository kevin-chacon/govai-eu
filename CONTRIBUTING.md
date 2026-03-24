# Contributing to govai-eu

Thank you for your interest in govai-eu. The most valuable thing anyone can do is **add tools to the registry** — you don't need to be a developer.

## What contributions are needed

The registry is the most valuable part of govai-eu. It currently contains 15 enterprise AI tools across 4 vendors. Every tool you add means the next person who runs govai gets an instant, accurate classification instead of relying on an LLM guess.

If you use a software tool that has AI features and it's not yet in the registry, you are the perfect person to add it — you already know what it does.

## How to add a tool to the registry

You don't need to install anything. You can do this entirely in your web browser on GitHub.

### Step 1: Go to the registry

Go to [github.com/kevin-chacon/govai-eu](https://github.com/kevin-chacon/govai-eu) and navigate to the `registry/tools/` folder.

### Step 2: Check if the vendor already has a file

Look at the existing files. They are named by vendor — for example, `microsoft.yaml` contains all Microsoft tools. If your tool's vendor already has a file, you will add your tool to that file. If not, you will create a new file.

### Step 3: Edit or create the file

- **If the vendor file exists:** Click on it, then click the pencil icon (✏️) in the top right to edit.
- **If the vendor file does not exist:** Click "Add file" → "Create new file". Name it `your-vendor.yaml` (all lowercase, e.g. `personio.yaml`).

### Step 4: Copy the template

Copy the contents of [`registry/tools/_template.yaml`](https://github.com/kevin-chacon/govai-eu/blob/main/registry/tools/_template.yaml) as your starting point. If you're adding to an existing file, paste it at the bottom.

### Step 5: Fill in each field

Here is what each field means:

| Field | What to put here |
|---|---|
| `name` | The full product name as people normally refer to it. Example: `"Salesforce Einstein Lead Scoring"` |
| `vendor` | The company that makes the tool. Example: `"Salesforce"` |
| `aliases` | Other names people use for this tool — abbreviations, vendor+short name combinations. Example: `["Einstein Lead Scoring", "SFDC Einstein"]` |
| `risk_tier` | The EU AI Act risk tier (see the classification guide below). One of: `UNACCEPTABLE`, `HIGH`, `LIMITED`, `MINIMAL`, `UNCLEAR` |
| `ai_features` | A list of the specific AI capabilities. Example: `["Predictive lead scoring", "Automated lead routing"]` |
| `decision_scope` | What autonomous decisions the tool makes. If the tool only makes suggestions that a human acts on, write that. If it makes no autonomous decisions, use `null`. Example: `"Scores and ranks leads automatically; sales reps see ranked list"` |
| `data_categories` | What types of data the AI processes. Example: `["Lead contact data", "Sales pipeline data"]` |
| `obligations` | What EU AI Act requirements apply for this risk tier. Example: `["Conformity assessment", "Risk management system"]` |
| `missing_docs_template` | What documentation is typically missing. Example: `["Conformity assessment report", "Bias audit results"]` |
| `source_url` | A URL to the vendor's documentation or product page where you found this information. Example: `"https://www.salesforce.com/products/einstein/overview/"` |
| `last_verified` | The month you checked this information, in `YYYY-MM` format. Example: `"2026-03"` |
| `notes` | Optional. Any caveats — for example, if the risk tier depends on how the tool is configured. Use `null` if there are no caveats. |

### Step 6: Submit your change

1. Scroll to the bottom of the page
2. Click **"Propose changes"**
3. On the next page, click **"Create pull request"**
4. Add a title like: `registry: add Personio HR`
5. Click **"Create pull request"** to submit

A maintainer will review your entry and merge it. You may receive feedback if anything needs adjusting.

## How to classify a tool correctly

The key question to ask is:

> **Does this tool make autonomous decisions that affect a person's rights, employment, or access to services?**

- **If yes → HIGH.** Examples: a tool that automatically screens CVs, scores credit applications, or routes customer complaints without human review.
- **If the tool interacts directly with users and they should know it's AI → LIMITED.** Examples: chatbots, AI-generated content tools.
- **If the tool assists a human who makes the final decision → probably MINIMAL.** Examples: a writing assistant that suggests text, a code completion tool, a spam filter.
- **If the risk depends on how the tool is configured → UNCLEAR.** Examples: a platform like Azure OpenAI where the risk depends on what the customer builds with it.

### Common mistakes

- **Don't classify everything as HIGH.** A writing assistant is not HIGH risk just because it uses AI. It becomes HIGH only if it makes autonomous decisions affecting people's rights.
- **Don't confuse "uses AI" with "makes autonomous decisions."** A search engine uses AI but doesn't make decisions about people's employment or credit.
- **Don't over-classify.** Over-classifying creates noise and undermines trust in the report. When genuinely unsure, use UNCLEAR and explain in the notes field what information would resolve it.

## What makes a good registry entry

- **Source URL links to real vendor documentation** — not a blog post or marketing page, but the product documentation or feature description
- **Risk tier matches the tool's actual decision-making scope** — not just its category. An HR tool that only generates reports is MINIMAL; one that screens candidates is HIGH.
- **Notes field explains any configuration-dependent factors** — if the tier could change based on how the tool is set up, say so
- **`last_verified` is set to the current month** — this tells future contributors when the entry was last checked

## Other ways to contribute

- **Open an issue if you think a classification is wrong.** Explain your reasoning and provide a link to vendor documentation that supports the change.
- **Open an issue to request a tool be added.** If you don't have time to add it yourself, describe the tool and what AI features it has.
- **Fix a typo or improve documentation.** Small improvements are always welcome.

## Code of conduct

Respectful, evidence-based disagreements about classifications are welcome — different people can reasonably disagree about risk tiers. Personal attacks, dismissive language, and bad-faith arguments are not acceptable.

## Development setup

If you want to contribute code (not required for registry contributions):

```bash
git clone https://github.com/kevin-chacon/govai-eu.git
cd govai-eu
pip install -e ".[dev]"
pytest
ruff check govai/
```
