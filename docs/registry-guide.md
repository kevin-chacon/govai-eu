# Registry Guide — How to Add Tools to govai-eu

This guide explains how to add an enterprise software tool to the govai-eu registry, including how to research a tool's AI features and classify it correctly under the EU AI Act.

The registry is a collection of YAML files in `registry/tools/`. Each file contains one or more tools from the same vendor. When someone runs `govai scan`, tools found in the registry get an instant, accurate classification — no LLM call needed.

## The YAML schema

Every tool entry follows the schema defined in `registry/schema.yaml`. Here is the template (`registry/tools/_template.yaml`) with annotations explaining each field:

```yaml
- name: ""
  # REQUIRED. Full product name as people normally refer to it.
  # Example: "Salesforce Einstein Lead Scoring"
  # Example: "Microsoft 365 Copilot"

  vendor: ""
  # REQUIRED. The company that makes the tool.
  # Example: "Salesforce"

  aliases: []
  # REQUIRED. Other names people might type when looking for this tool.
  # Include abbreviations, alternative product names, and common
  # vendor+short name combinations. govai uses these for matching.
  # Example: ["Einstein Lead Scoring", "SFDC Einstein Lead Scoring"]

  risk_tier: "UNCLEAR"
  # REQUIRED. The EU AI Act risk tier. Must be one of:
  #   UNACCEPTABLE | HIGH | LIMITED | MINIMAL | UNCLEAR
  # See the classification guide below to choose correctly.

  ai_features: []
  # REQUIRED. Specific AI capabilities the tool provides.
  # Be concrete — "AI-powered lead scoring" is better than "uses AI".
  # Example: ["Predictive lead scoring", "Automated lead routing"]

  decision_scope: null
  # REQUIRED (can be null). What autonomous decisions the tool makes.
  # If the tool only suggests and a human decides, say so.
  # If no autonomous decisions, set to null.
  # Example: "Scores and ranks leads automatically; sales reps see ranked list"

  data_categories: []
  # REQUIRED. Types of data the AI processes.
  # Example: ["Lead contact data", "Sales pipeline data", "Email metadata"]

  obligations: []
  # REQUIRED. EU AI Act obligations for the assigned risk tier.
  # For HIGH: conformity assessment, technical documentation, risk management, etc.
  # For LIMITED: transparency disclosure.
  # For MINIMAL: no specific obligations.
  # Example: ["Conformity assessment", "Risk management system"]

  missing_docs_template: []
  # REQUIRED. Documentation that is typically absent for this tool.
  # This tells the report reader what they probably need to create.
  # Example: ["Conformity assessment report", "Bias audit results"]

  source_url: ""
  # REQUIRED. URL to the vendor's product documentation, feature page,
  # or help article where you found this information.
  # Must be a real, working link — not a marketing landing page.
  # Example: "https://help.salesforce.com/s/articleView?id=sf.einstein_lead_scoring.htm"

  last_verified: ""
  # REQUIRED. The month you checked this information, in YYYY-MM format.
  # Example: "2026-03"

  notes: null
  # OPTIONAL. Caveats about when the risk tier might be different,
  # configuration-dependent factors, or anything the reader should know.
  # Example: "Risk tier depends on whether automated routing is enabled"
```

## EU AI Act risk tier guide

### UNACCEPTABLE — Prohibited

**Definition:** The AI system is banned under the EU AI Act. No deployment is permitted.

**What makes a tool fall here:** The tool performs social scoring by public authorities, real-time biometric surveillance in public spaces, subliminal behavioural manipulation, or exploitation of vulnerable groups.

**Real-world examples:** Government social credit scoring systems. Real-time facial recognition surveillance in public spaces. AI systems designed to manipulate behaviour below a person's awareness.

**Key question:** *Does this system score, surveil, or manipulate people in ways the EU AI Act explicitly prohibits?*

### HIGH — Strict obligations apply

**Definition:** The AI system makes or significantly influences decisions that affect people's rights, employment, access to services, or safety. Organisations must comply with technical documentation, risk management, human oversight, and audit logging requirements.

**What makes a tool fall here:** The tool autonomously makes decisions about hiring, firing, promotion, credit scoring, insurance pricing, university admissions, or access to essential services — without meaningful human review of each decision.

**Real-world examples:**
- **Salesforce Einstein Lead Scoring** with automated routing (if leads are routed without human review)
- **Workday HCM** with AI-powered candidate screening (if it filters out candidates automatically)
- **SAP SuccessFactors Recruiting** with automated shortlisting
- Credit scoring tools that approve or deny applications

**Key question:** *Does this tool make autonomous decisions that affect a person's rights, employment, or access to services?*

### LIMITED — Transparency obligations

**Definition:** The AI system has transparency obligations. Users must be informed that they are interacting with AI or that content was AI-generated.

**What makes a tool fall here:** The tool interacts directly with users in a way where they might not realise it's AI, or it generates content that could be mistaken for human-created.

**Real-world examples:**
- **HubSpot ChatSpot** (conversational AI for customer interactions)
- Customer support chatbots
- AI-generated marketing content tools
- Emotion recognition in customer service

**Key question:** *Does this tool interact with people who should know they're dealing with AI?*

### MINIMAL — No specific obligations

**Definition:** The AI system has no specific EU AI Act obligations beyond general good practice.

**What makes a tool fall here:** The tool uses AI but does not make autonomous decisions about people and does not interact with users in a way that requires transparency disclosure. A human reviews and acts on the AI's output.

**Real-world examples:**
- **GitHub Copilot** (suggests code; developer reviews all output)
- **Notion AI** (drafts content; user reviews and edits)
- Spam filters
- Search and recommendation engines
- General writing assistants

**Key question:** *Does this tool just assist a human who makes the final decision?*

### UNCLEAR — Requires verification

**Definition:** The risk tier depends on how the tool is configured or deployed and cannot be determined from publicly available information alone.

**What makes a tool fall here:** The tool is a platform or configurable system where the risk depends on specific customer use cases, or insufficient public information is available.

**Real-world examples:**
- **Azure OpenAI Service** (risk depends on what the customer builds)
- **Google Cloud Vertex AI** (platform; risk depends on application)
- Custom internal tools with limited documentation
- Tools where the vendor does not clearly describe AI features

**Key question:** *Is there not enough information to determine the risk, or does the risk depend on configuration?*

## How to research a tool's AI features

Before classifying a tool, you need to understand what its AI actually does. Here is where to look:

1. **Vendor product page** — The product overview usually lists key features including AI capabilities.
2. **Help centre or documentation** — Search for "AI", "machine learning", "automated", or "intelligent" in the vendor's help documentation.
3. **Release notes** — Vendors often announce new AI features in release notes or changelogs.
4. **Trust and safety pages** — Some vendors publish AI principles or responsible AI documentation that describes how their AI makes decisions.

**What to look for:**
- Does the tool make **autonomous decisions** (acts on its own), or does it make **suggestions** that a human acts on?
- What **data** does the AI process? Personal data? Employment data? Financial data?
- Can a **human override** the AI's output, or does it act automatically?
- Does the tool **interact directly with end users** (customers, candidates, patients)?

The distinction between "makes autonomous decisions" and "makes suggestions" is the most important factor in classification.

## Common classification mistakes

### Mistake 1: Classifying all AI tools as HIGH

Most AI tools are MINIMAL or LIMITED. A tool is only HIGH if it makes autonomous decisions affecting people's rights, employment, or access to services. A writing assistant that suggests text is MINIMAL — even though it "uses AI".

### Mistake 2: Classifying a platform as one tier

Large platforms like SAP, Salesforce, or Microsoft 365 have many modules with different AI features. Each module should be classified separately:

- **SAP Business AI for Procurement** (automates purchase order matching) → likely MINIMAL
- **SAP SuccessFactors Recruiting** (AI candidate screening with automated shortlisting) → HIGH
- **SAP Conversational AI** (customer-facing chatbot) → LIMITED

When adding a platform, create separate entries for each distinct AI-powered module rather than one entry for the entire platform.

### Mistake 3: Confusing "uses AI" with "makes autonomous decisions"

Using AI does not automatically mean HIGH risk. The key is whether the AI **acts autonomously on decisions that affect people**:

| Tool | Uses AI? | Autonomous decisions about people? | Tier |
|---|---|---|---|
| Spam filter | Yes | No — filters emails, not people | MINIMAL |
| Code completion | Yes | No — developer decides | MINIMAL |
| Chatbot | Yes | No — but must disclose it's AI | LIMITED |
| CV screener that filters candidates | Yes | Yes — affects employment access | HIGH |

## Examples of completed registry entries

### HIGH risk — HR screening tool

```yaml
- name: "Workday HCM AI Recruiting"
  vendor: "Workday"
  aliases:
    - "Workday Recruiting AI"
    - "Workday AI candidate screening"
  risk_tier: "HIGH"
  ai_features:
    - "Automated candidate ranking and shortlisting"
    - "Skills inference from resume parsing"
    - "Predictive candidate fit scoring"
  decision_scope: "Ranks and shortlists candidates autonomously. Hiring managers see pre-filtered list."
  data_categories:
    - "Candidate personal data"
    - "Resume content"
    - "Employment history"
    - "Skills and qualifications"
  obligations:
    - "Conformity assessment (Article 43)"
    - "Technical documentation (Article 11)"
    - "Risk management system (Article 9)"
    - "Human oversight mechanism (Article 14)"
    - "Audit logging of automated decisions"
    - "Transparency notice to candidates"
  missing_docs_template:
    - "Conformity assessment report"
    - "Bias audit results"
    - "Technical documentation package"
    - "Candidate transparency notice"
  source_url: "https://www.workday.com/en-us/products/human-capital-management.html"
  last_verified: "2026-03"
  notes: "Risk tier is HIGH only when automated shortlisting is enabled. If Workday is used for manual HR workflows without AI screening, the AI features may be MINIMAL."
```

### LIMITED risk — Customer-facing chatbot

```yaml
- name: "HubSpot ChatSpot"
  vendor: "HubSpot"
  aliases:
    - "ChatSpot"
    - "HubSpot AI chatbot"
  risk_tier: "LIMITED"
  ai_features:
    - "Conversational AI for customer interactions"
    - "CRM data queries via natural language"
    - "Content generation from prompts"
  decision_scope: null
  data_categories:
    - "CRM contact data"
    - "Conversation content"
  obligations:
    - "Transparency disclosure — users must be informed they are interacting with AI"
  missing_docs_template:
    - "AI disclosure notice for end users"
  source_url: "https://www.hubspot.com/products/chatspot"
  last_verified: "2026-03"
  notes: null
```

### MINIMAL risk — Writing assistant

```yaml
- name: "Notion AI"
  vendor: "Notion"
  aliases:
    - "Notion AI assistant"
  risk_tier: "MINIMAL"
  ai_features:
    - "Document summarisation"
    - "Content drafting from prompts"
    - "Action item extraction"
  decision_scope: "Generates content suggestions; user reviews all output."
  data_categories:
    - "Workspace documents and notes"
  obligations:
    - "No specific EU AI Act obligations for MINIMAL risk"
  missing_docs_template:
    - "No mandatory documentation required"
  source_url: "https://www.notion.so/product/ai"
  last_verified: "2026-03"
  notes: null
```

## How to handle tools that depend on configuration

Some tools have a risk tier that depends on how they are configured. For these, use `UNCLEAR` and explain in the `notes` field what configuration determines the tier.

**Example:**

```yaml
- name: "Azure OpenAI Service"
  vendor: "Microsoft"
  aliases:
    - "Azure OpenAI"
    - "AOAI"
  risk_tier: "UNCLEAR"
  ai_features:
    - "Large language model hosting and inference"
    - "Custom model fine-tuning"
    - "Embedding generation"
  decision_scope: "Platform — decision scope depends entirely on customer application."
  data_categories:
    - "Varies by customer deployment"
  obligations:
    - "Depends on deployment use case — may range from MINIMAL to HIGH"
  missing_docs_template:
    - "Deployment-specific risk assessment"
    - "Use case documentation"
  source_url: "https://learn.microsoft.com/en-us/azure/ai-services/openai/overview"
  last_verified: "2026-03"
  notes: "Azure OpenAI is a platform, not an application. Risk tier depends on what the customer builds. A chatbot deployment would be LIMITED. A hiring screening tool built on Azure OpenAI would be HIGH. Classify the specific application, not the platform."
```

The `notes` field should answer: *"What would someone need to know to determine the correct tier?"*
