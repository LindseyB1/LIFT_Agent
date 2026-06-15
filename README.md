# Project 3 Final AI Application Shell

## Working Title

Replace this with the final Project 3 title.

Example:
**Project 3 Final: Adaptive AI Decision Support Agent**

## Purpose

This project is a final AI application shell built from the lessons learned in Project 1 and Project 2.

Project 1 focused on foundational AI application concepts such as prompts, grounding, role-based instructions, structured outputs, constraints, and evaluation.

Project 2, TrendLens AI, improved that foundation by adding a Streamlit interface, deployment readiness, authentication/demo mode, saved outputs, monitoring logic, feedback logging, evaluation records, and a real model-callable tool workflow.

Project 3 should combine those lessons into a cleaner final product:
- Clear user problem.
- Real LLM decision point.
- Real tool/function call.
- Honest routing explanation.
- Evaluation records.
- Build log.
- Security/secrets handling.
- Deployed Streamlit app.
- README that does not overclaim.

## Key Project 3 Lesson Applied

The main Project 2 feedback was that changing prompt text is not the same as true model routing. For Project 3, this shell includes:

1. An LLM router that chooses a route based on the user request.
2. A route-to-model selection function.
3. A model-callable tool named `analyze_project_request`.
4. A tool trace shown in the app.
5. An evaluation record saved to `Tests/eval_results.md`.

## Suggested File Structure

```text
Project3_Final_Shell/
├── .streamlit/
│   └── config.toml
├── assets/
│   └── README_assets.md
├── Data/
│   └── sample_input.md
├── Docs/
│   └── project3_design_notes.md
├── Evidence/
│   └── test_run_notes.md
├── Monitoring/
│   └── example_monitoring_log.md
├── Outputs/
│   └── example_output.md
├── Prompts/
│   ├── router_prompt.md
│   └── system_prompt.md
├── scripts/
│   └── create_project_snapshot.py
├── Tests/
│   ├── eval_results.md
│   └── test_smoke.py
├── app.py
├── auth.py
├── p3_tools.py
├── monitoring.py
├── scheduler_worker.py
├── security_utils.py
├── ui_components.py
├── BUILD_LOG.md
├── API_PROMPT_LOG.md
├── README.md
├── requirements.txt
└── .gitignore
```

## Local Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Secrets

Do not commit API keys.

Use one of these:

### Local `.env`

```text
OPENAI_API_KEY=your_key_here
```

### Streamlit secrets

Create:

```text
.streamlit/secrets.toml
```

Add:

```toml
OPENAI_API_KEY = "your_key_here"
# LIFT Agent - Provider Matching & Warm Outreach Workflow

## Project Overview

**LIFT Agent** (Locate. Identify. Follow-up. Track.) is an AI-supported provider matching and warm outreach workflow built for Project 3 in a Generative AI course.

**LIFT is a draft tool using synthetic/public data only.** It helps match users to resources, identify access barriers, draft outreach messages, and track follow-ups—all requiring human review and approval at every step.

### What LIFT Does

- 📍 **Locate:** Match users to providers based on need, location, radius, availability, and eligibility.
- 🔍 **Identify:** Highlight gaps (eligibility barriers, hours, transportation, documentation, verification needs).
- ✉️ **Follow-up:** Draft warm outreach emails, call scripts, and confirmation checklists.
- 📋 **Track:** Generate follow-up tracker rows and export as CSV.

### What LIFT Does NOT Do

- ❌ Send emails automatically
- ❌ Call providers
- ❌ Monitor voicemail or scan inboxes
- ❌ Store private case files without explicit consent
- ❌ Claim to be the final authority on resource fit
- ❌ Use real-world operational data (synthetic data only)

---

## Deployed App

**[Open LIFT Agent on Streamlit](https://lift-agent.streamlit.app/)**

---

## GitHub Repository

**[LindseyB1/LIFT_Agent](https://github.com/LindseyB1/LIFT_Agent)**

---

## Getting Started Locally

### 1. Clone the Repository

```bash
git clone https://github.com/LindseyB1/LIFT_Agent.git
cd LIFT_Agent
```

### 2. Set Up Python Environment

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root (do NOT commit this):

```bash
OPENAI_API_KEY=your_openai_api_key_here
P3_DEFAULT_MODEL=gpt-4o-mini
```

**For Streamlit Cloud deployment**, add the key via **Secrets** instead of `.env`:

```
Settings > Secrets > Add secret
OPENAI_API_KEY = your_key_here
```

### 5. Run the App Locally

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Using LIFT Agent

### Privacy & Consent First

Before generating a plan, you **must** check all four required boxes:

1. ☑ I understand this draft uses public or synthetic information only.
2. ☑ I will not enter private, classified, restricted, protected, or sensitive personal information.
3. ☑ I understand this app does not send emails, contact providers, scan inboxes, monitor phones, or access voicemail.
4. ☑ I understand AI-generated outreach must be reviewed and approved by a human before use.

### Step 1: Locate the Need

- **What does the user need help with?**  
  Example: _"I need a food pantry near Grand Rapids, but I work third shift and have limited transportation."_

- **Resource Category:** Select from 11 categories (Food, Housing, Transportation, Legal, Veteran, etc.)

- **Urgency:** Routine, Soon, Urgent, or Crisis.

### Step 2: Identify Location & Access Limits

- **Primary location:** Where the user is based (e.g., Grand Rapids, MI).
- **Additional locations:** Other areas to search (optional).
- **Search radius in miles:** How far to look (5–100 miles).

### Step 3: Fit & Eligibility Context

- **User type:** Service member, Veteran, Military-connected family, Community member, etc.
- **Transportation:** Yes, No, Limited, Public transit only.
- **24/7 or after-hours needed?** No, Yes, Not sure.
- **Documents available?** Yes, No, Not sure.

### Step 4: Follow-Up Outputs

Select which outputs to generate:
- Resource fit summary
- Gap analysis
- Three contingency plans
- User-approved outreach draft
- Tracker rows
- System gap notes
- Map view
- CSV tracker download

### Step 5: Generate & Review

Click **Generate LIFT Plan**. The app will:

1. **AI Routing Decision:** LLM selects the best route (if API key is available).
2. **Custom Tool Call:** Runs a model-callable tool to analyze resources and gaps.
3. **Show Results:**
   - Agent Decision Trace (why the route was chosen)
   - Matched resources table
   - Eligibility and access barriers
   - Three contingency plans

### Step 6: Select Providers & Draft Outreach

1. **Select providers** you want to pursue (checkboxes).
2. **Review/edit outreach** for each selected provider:
   - Subject line
   - Email draft
   - Call script
   - Confirmation checklist
   - Follow-up date
3. **Download all drafts** as a single text file.

### Step 7: Track Follow-Ups

- **Follow-up Tracker** shows provider name, category, contact method, status, and next step.
- **Download Tracker CSV** for spreadsheet management.

---

## Agentic Workflow Explanation

LIFT is not a static tool or simple chatbot. It demonstrates a real **agentic workflow**:

```
User Input
	↓
[AI Router Decision]  ← LLM chooses the best route based on context
	↓
[Custom Tool Call]    ← Model calls a function (not just text generation)
	↓
[Tool Execution]      ← Analyzes resources, gaps, contingencies
	↓
[Tool Result]         ← Returns structured data
	↓
[Human Approval]      ← User reviews outreach, selects providers
	↓
[Outreach Export]     ← Human-approved drafts (not auto-sent)
```

### Agent Decision Trace

Every time you generate a plan, LIFT shows:

- **Selected Route:** What the LLM decided (location_radius_match, gap_analysis, outreach_email, etc.)
- **Reason:** Why that route was chosen
- **Confidence:** High, Medium, or Low
- **Evidence:** Key factors that influenced the decision

---

## MCP-Style Tool Explanation

LIFT includes a **Model Context Protocol (MCP)-style tool placeholder** called `check_provider_website_mcp_tool`.

### What It Does

```python
check_provider_website_mcp_tool(
	provider_name="Kent County Community Food Pantry",
	website_url="https://example.org/food",
	category="Food / Basic Needs",
	location="Grand Rapids, MI"
)
```

### Tool Output

```json
{
  "status": "reachable",
  "confidence": "high",
  "notes": "Website appears to be live. Main page loads. Phone contact visible.",
  "website_components_found": ["phone", "email", "hours", "eligibility"],
  "timestamp": "2026-06-14 14:23:00 UTC",
  "limitations": [
	"Does not perform real web scraping.",
	"Results from synthetic/demo data only.",
	"Assumes public websites only."
  ]
}
```

### Current Implementation

For **safety**, the tool uses **synthetic/demo results**. A production version could:

- Validate website reachability via HTTP HEAD/GET
- Parse public contact information
- Verify hours of operation
- Flag outdated contact data

---

## Privacy & Consent Limits

### What LIFT Assumes

- **Synthetic data only:** All resource records are for demonstration; not linked to real operational systems.
- **Public information only:** No private, classified, restricted, protected, or sensitive personal information.
- **No automation:** Nothing is sent or accessed automatically.
- **Human approval required:** Every outreach draft requires human review before use.

### Session-Only Output (Optional)

Users can opt for **session-only history**, which:
- Keeps outputs in browser memory only
- Does not save to disk
- Clears when the session ends

### Privacy Settings

Users can enable/disable:
- Session-only output history
- Privacy and consent notes in generated plan
- Basic public provider website checks

---

## Known Limitations

1. **Synthetic Data:** Resource records are demo-only. Not real operational directory.
2. **No Real Verification:** Website checks do not perform actual HTTP requests in this draft.
3. **No Real Outreach:** Drafts are not sent automatically; human must copy/paste.
4. **Limited Eligibility Logic:** Barriers are flagged based on heuristics, not true intake forms.
5. **No Authentication:** Anyone can use the draft app; future versions would add login/role-based access.
6. **No Audit Log:** Not designed for HIPAA/compliance auditing yet.

---

## Data Files

### Synthetic Resource Data

- **File:** `app.py` (function: `synthetic_resource_data()`)
- **Records:** 8 example resources across 6 categories
- **Uses:** Kent County, Michigan (Grand Rapids area)

### Project Structure

```
LIFT_Agent/
├── app.py                       # Main Streamlit app
├── auth.py                      # Authentication placeholder
├── monitoring.py                # Monitoring / logging
├── p3_tools.py                  # Utility functions (keywords, complexity)
├── security_utils.py            # Security helpers
├── ui_components.py             # UI helper functions
├── scheduler_worker.py          # Background job placeholder
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── .gitignore                   # Git ignore (includes .env)
├── .streamlit/
│   └── config.toml              # Streamlit config
├── Docs/
│   └── project3_design_notes.md # Design decisions
├── Tests/
│   └── eval_results.md          # Evaluation records
├── Prompts/
│   ├── router_prompt.md         # LLM router prompt
│   └── system_prompt.md         # System context
└── Evidence/
	└── test_run_notes.md        # Test execution notes
```

---

## Deployment to Streamlit Cloud

### 1. Push to GitHub

```bash
git add .
git commit -m "Final LIFT Agent submission"
git push origin main
```

### 2. Connect GitHub Repo to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New App**
3. Select repo: `LindseyB1/LIFT_Agent`
4. Select branch: `main`
5. Set main file path: `app.py`

### 3. Add Secrets

1. Click **Deploy** → **Settings** (gear icon)
2. Go to **Secrets**
3. Add:
   ```
   OPENAI_API_KEY = your_key_here
   P3_DEFAULT_MODEL = gpt-4o-mini
   ```

### 4. Deploy

Streamlit automatically deploys whenever you push to `main`.

---

## Development & Testing

### Run Tests

```bash
python -m pytest Tests/test_smoke.py -v
```

### Local Demo Mode

If no `OPENAI_API_KEY`, the app runs in **Demo Mode** with synthetic tool results.

### Monitoring

- **File:** `monitoring.py`
- Logs request timestamps, model decisions, tool results
- Evaluates output quality and user feedback

---

## Frequently Asked Questions

### Q: Will LIFT actually send an email?

**A:** No. LIFT generates draft text only. You must copy/paste into your email client and press Send yourself.

### Q: Can I use LIFT with real client data?

**A:** No. LIFT is designed for synthetic/public data only. Using real private data violates the consent agreement and defeats the purpose of the draft.

### Q: What if I don't have an OpenAI API key?

**A:** LIFT runs in Demo Mode. It still generates outreach and trackers, but the AI routing decision is replaced with a labeled fallback decision. Full LLM routing requires an API key.

### Q: Can LIFT scan provider websites or call them?

**A:** Not in this version. The MCP tool is a placeholder showing how such functionality could be structured safely. Real web scraping is not implemented.

### Q: How do I know if a provider is actually available?

**A:** LIFT flags resources as "Needs verification." You must verify by:
1. Calling the provider directly
2. Visiting their official website
3. Asking for recent confirmation from someone else who used the service

### Q: Can I export the results?

**A:** Yes:
- Download outreach drafts as a `.txt` file
- Download tracker as a `.csv` file
- Copy/paste the full report from the app

---

## Contact & Feedback

- **Course:** Generative AI (GVSU)
- **Project:** Project 3 - Final AI Application
- **Author:** [Your Name]
- **GitHub:** [LindseyB1/LIFT_Agent](https://github.com/LindseyB1/LIFT_Agent)
- **Issues & Questions:** Open a GitHub issue

---

## License

This project is provided as-is for educational purposes. Synthetic data is for demonstration only.

---

## Appendix: Understanding the Route Options

When LIFT generates a plan, it selects one of these routes:

| Route | When Used | Example |
|-------|-----------|---------|
| `resource_match` | User mainly needs matching resources | "Find me a food pantry" |
| `location_radius_match` | Location, distance, or multiple search areas matter | "Find a food pantry near these three cities" |
| `gap_analysis` | Access barriers, eligibility, hours, transportation matter | "I need 24/7 support but no transportation" |
| `validation_review` | Need to verify phone, website, hours, status | "Is that office still open?" |
| `outreach_email` | Need to draft a provider outreach message | "Draft a warm email to the housing office" |
| `tracker_generation` | Need follow-up rows or action tracking | "Help me track who I need to call back" |
| `system_gap_brief` | Need a higher-level gap report | "What barriers are common across providers?" |
| `fallback_review` | Unclear request | (Catch-all default) |

---

**Last Updated:** June 14, 2026  
**Version:** 1.0 (Project 3 Draft)
