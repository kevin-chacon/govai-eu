# govai — AI System Inventory Report

**Generated:** 2026-03-23 19:48 UTC  
**Input file:** tests\fixtures\sample_tools.csv  
**Tools analysed:** 6

## Risk Summary

| Risk Tier | Count | Percentage |
|-----------|-------|------------|
| HIGH | 1 | 17% |
| LIMITED | 2 | 33% |
| MINIMAL | 1 | 17% |
| UNCLEAR | 2 | 33% |

## HIGH — Salesforce Einstein Lead Scoring (Salesforce)

**Confidence:** registry_match

**AI Features:**
- Predictive lead scoring based on historical conversion data
- Automatic lead prioritisation
- Lead routing recommendations

**Decision Scope:** Autonomously scores and ranks leads, which directly determines sales team attention and resource allocation. Can route leads to specific teams based on predicted conversion likelihood.


**Data Processed:**
- Lead contact information
- Lead engagement and behavioural data
- Historical sales conversion data
- Firmographic data

**EU AI Act Obligations:**
- Conformity assessment before deployment
- Risk management system
- Data governance and quality controls
- Technical documentation
- Record-keeping and logging
- Transparency to affected individuals
- Human oversight mechanism

**Missing Documentation:**
- Conformity assessment report
- Algorithmic impact assessment for lead routing
- Data quality documentation
- Human oversight procedures for lead scoring overrides

**Notes:** HIGH risk because autonomous lead routing can determine access to commercial services and affects individuals' economic outcomes.


---

## LIMITED — Microsoft 365 Copilot (Microsoft)

**Confidence:** registry_match

**AI Features:**
- Document drafting and summarisation
- Email composition suggestions
- Presentation generation from prompts
- Meeting transcript summarisation
- Data analysis in Excel via natural language

**Decision Scope:** Generates content suggestions; human reviews and approves all output before use.

**Data Processed:**
- Business documents and emails
- Meeting transcripts
- Spreadsheet data
- Presentation content

**EU AI Act Obligations:**
- Transparency: disclose AI-generated content to recipients
- Mark AI-generated or AI-assisted content where applicable

**Missing Documentation:**
- AI usage disclosure policy for outbound communications
- Internal guidelines on reviewing AI-generated content

**Notes:** Risk tier is LIMITED because Copilot generates content that a human reviews before sending. If configured to send content autonomously (e.g. auto-reply), risk may increase to HIGH.


---

## LIMITED — HubSpot ChatSpot (HubSpot)

**Confidence:** registry_match

**AI Features:**
- Conversational AI for CRM queries
- Natural language CRM data lookup
- AI-assisted report generation
- Customer-facing chat interactions

**Decision Scope:** Responds to queries and generates reports; does not make autonomous business decisions.

**Data Processed:**
- CRM data (contacts, deals, companies)
- User queries and conversation history

**EU AI Act Obligations:**
- Transparency: disclose AI nature to users interacting with chatbot
- Mark AI-generated responses in customer communications

**Missing Documentation:**
- Chatbot AI disclosure notice
- Customer-facing AI transparency policy

**Notes:** LIMITED because it is a chatbot that must disclose its AI nature. Transparency obligation under EU AI Act Article 50.


---

## MINIMAL — GitHub Copilot (Microsoft)

**Confidence:** registry_match

**AI Features:**
- Code completion and suggestion
- Natural language to code generation
- Code explanation and documentation
- Pull request summarisation

**Decision Scope:** Suggests code completions; developer reviews and accepts or rejects each suggestion.

**Data Processed:**
- Source code
- Code comments and documentation
- Repository metadata

**EU AI Act Obligations:**
- No specific EU AI Act obligations for MINIMAL risk
- Voluntary: follow codes of conduct for AI development tools

**Missing Documentation:**
- AI-assisted code review policy
- Intellectual property guidelines for AI-generated code

**Notes:** MINIMAL risk — code suggestions with full developer oversight. No autonomous decisions affecting natural persons.


---

## UNCLEAR — Google Vertex AI (Google)

**Confidence:** registry_match

**AI Features:**
- Custom ML model training and deployment
- AutoML for structured and unstructured data
- Generative AI model hosting (PaLM, Gemini)
- MLOps and model management

**Decision Scope:** No autonomous decisions identified

**Data Processed:**
- Depends entirely on deployment configuration

**EU AI Act Obligations:**
- Depends on downstream application risk tier
- Platform-level: maintain deployment and access logs

**Missing Documentation:**
- Downstream application risk assessment
- Per-deployment data processing documentation

**Notes:** Vertex AI is a platform, not a product. Risk tier depends entirely on what the customer deploys. Each application built on Vertex AI must be assessed individually.


---

## UNCLEAR — Zoom AI Companion

**Confidence:** inferred

**Decision Scope:** No autonomous decisions identified

**Notes:** Not in registry; LLM fallback disabled

---


*This report is generated by govai and is a starting point for EU AI Act compliance review. It is not a legal opinion. Classifications marked 'inferred' should be verified. govai is open source: github.com/kevin-chacon/govai-eu*
