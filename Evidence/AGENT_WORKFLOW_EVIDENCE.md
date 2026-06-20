# LIFT Agent - Agentic Workflow Evidence

**Project:** Project 3 - LIFT Agent (Locate, Identify, Follow-up, Track)  
**Date:** June 14, 2026  
**Purpose:** Document the agentic workflow and model-callable tool execution

---

## Agentic Workflow Demonstration

LIFT Agent demonstrates a real agentic workflow, not just text generation:

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Input & Context                         │
│  Need: Food pantry with 24/7 access near Grand Rapids            │
│  Location: Grand Rapids, MI + Wyoming, MI (25 mile radius)       │
│  Context: Third-shift worker, limited transportation              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 1: AI Router Decision (LLM Model)                  │
│                                                                  │
│  Router Route: "gap_analysis"                                   │
│  Reason: "Access barriers matter: 24/7 need + transportation    │
│           limits + third-shift schedule"                         │
│  Confidence: "high"                                             │
│  Tool Used: "analyze_resource_gaps_and_build_contingency_plan"  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│      STEP 2: Model Requests Custom Tool (Function Call)         │
│                                                                  │
│  Tool Name: "analyze_resource_gaps_and_build_contingency_plan"  │
│  Tool Status: Model-callable function via OpenAI tools API      │
│  Inputs:                                                         │
│    - user_need: "Food pantry with 24/7 access"                  │
│    - resource_category: "Food / Basic Needs"                    │
│    - primary_location: "Grand Rapids, MI"                       │
│    - additional_locations: ["Wyoming, MI"]                      │
│    - radius_miles: 25                                           │
│    - context:                                                   │
│        * needs_24_7: "Yes"                                      │
│        * transportation: "Limited"                              │
│        * audience: "Community member"                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│    STEP 3: Custom Tool Execution (Local Function)               │
│                                                                  │
│  Function: analyze_resource_gaps_and_build_contingency_plan()   │
│  Execution Mode: Synchronous local call                         │
│  Processing:                                                    │
│    1. Filter resources by category & location (5 matches)       │
│    2. Identify eligibility barriers                             │
│    3. Flag 24/7 gaps (3 resources are business-hours only)      │
│    4. Flag transportation barriers (2 resources)                │
│    5. Build 3 contingency plans                                 │
│    6. Generate outreach draft                                   │
│    7. Create tracker rows                                       │
│    8. Summarize system gaps                                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│          STEP 4: Tool Result Returned to Model                  │
│                                                                  │
│  Tool Result Keys:                                              │
│    ✓ matched_resources (5 food pantries)                        │
│    ✓ fit_concerns (3 main concerns)                             │
│    ✓ eligibility_barriers (2 identified)                        │
│    ✓ access_barriers (3 identified)                             │
│    ✓ twenty_four_seven_gaps (3 identified)                      │
│    ✓ validation_flags (6 resources need verification)           │
│    ✓ contingency_plans (3 fallback options)                     │
│    ✓ outreach_email_draft (formatted for review)                │
│    ✓ tracker_rows (5 row entries)                               │
│    ✓ system_gap_notes (3 summary items)                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│      STEP 5: User Review & Selection (Human Approval)           │
│                                                                  │
│  User Reviews:                                                  │
│    ✓ Agent Decision Trace (why gap_analysis was chosen)         │
│    ✓ Matched resources table                                    │
│    ✓ Identified barriers (24/7, transportation, etc.)           │
│    ✓ Three contingency plans                                    │
│                                                                  │
│  User Actions:                                                  │
│    1. Selects 2-3 providers to pursue                           │
│    2. Reviews/edits outreach drafts                             │
│    3. Confirms eligibility & hours                              │
│    4. Sets follow-up dates                                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 6: Outreach Export (Not Automated)                 │
│                                                                  │
│  Export Format: Human-reviewed draft (text file)                │
│  Contains:                                                      │
│    - Subject lines (editable)                                   │
│    - Email drafts (editable)                                    │
│    - Call scripts (editable)                                    │
│    - Confirmation checklists                                    │
│    - Follow-up dates                                            │
│                                                                  │
│  Next Step: User copy/pastes into email client and hits SEND    │
│  App Role: DRAFT GENERATOR, NOT SENDER                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Agentic Decisions

### 1. Router Decision: "gap_analysis"

**Why?**
- User explicitly stated "24/7 access" needed
- User stated "limited transportation"
- Context indicates access barriers are the problem, not just matching

**Evidence:**
```
"Confidence": "high"
"Evidence": [
  "User has explicit 24/7 requirement",
  "User has transportation constraints",
  "Multiple barriers flagged (hours + transportation + documentation)",
  "Gap analysis is most helpful route"
]
```

### 2. Tool Selection: "analyze_resource_gaps_and_build_contingency_plan"

**Why?**
- Gap analysis route requires structured analysis of barriers
- Tool accepts context (needs_24_7, transportation, etc.)
- Tool outputs structured gaps + contingency plans

**Evidence:**
```
Tool traces show:
- 3 resources flagged for "not 24/7"
- 2 resources flagged for "transportation required"
- 1 resource flagged for "eligibility documentation"
- 3 contingency plans auto-generated
```

### 3. Contingency Plans Generated

**Plan A:** Use the closest matching resource first (if available)
**Plan B:** Use a 24/7 or remote navigation fallback (211, 988, etc.)
**Plan C:** Escalate the access gap (track repeated barriers)

---

## External Data and MCP-Style Tool: check_provider_website_mcp_tool

Before the model writes the final LIFT plan, the app calls the OpenStreetMap Nominatim public search API and normalizes returned JSON into resource rows. The Agent Decision Trace shows the endpoint, query strings, result count, errors, and whether fallback data was used.

### Structure

```python
def check_provider_website_mcp_tool(
    provider_name: str,
    website_url: str,
    category: str,
    location: str
) -> Dict:
```

### Input Example

```python
check_provider_website_mcp_tool(
    provider_name="Pleasant Hearts Pet Food Pantry",
    website_url="https://www.pleasantheartspetfoodpantry.org/",
    category="Food / Basic Needs",
    location="Grand Rapids, MI"
)
```

### Output Example

```json
{
  "tool_name": "check_provider_website_mcp_tool",
  "provider_name": "Pleasant Hearts Pet Food Pantry",
  "website_url": "https://www.pleasantheartspetfoodpantry.org/",
  "status": "reachable",
  "http_status": 200,
  "confidence": "high",
  "notes": "HTTP 200; content type text/html. Found public page signals: phone_or_contact, email.",
  "website_components_found": [
    "phone_or_contact",
    "email"
  ],
  "timestamp": "2026-06-14 14:23:00 UTC",
  "limitations": [
    "This is a basic public HTTP check only.",
    "HTTP reachability is not proof that services are currently available.",
    "Does not access login-required pages."
  ],
  "recommendation": "Always verify by phone before referring user."
}
```

### Current Implementation

Uses **real public HTTP requests** when a provider URL is available:
- Status: `"reachable"`, `"unreachable"`, or `"unknown"`
- Confidence: `"high"`, `"medium"`, or `"low"`
- Components: Scans public HTML for contact, email, hours, appointment, eligibility, or intake signals

**NOT implemented (for safety):**
- DOM parsing / JavaScript execution
- Credential checking
- Behind-login content

**Future production version could:**
- Validate reachability via HTTP HEAD/GET
- Parse public pages for contact info
- Flag 404 or SSL errors
- Track response times

---

## Human Approval Points

### 1. Consent Section
**Required before generating:**
- Synthetic data acknowledgment
- No sensitive information agreement
- No automation confirmation
- Human approval requirement

### 2. Provider Selection
**Required before outreach:**
- User selects 2-3 providers to pursue
- App does NOT generate for all 5

### 3. Outreach Review
**Before downloading drafts:**
- Email draft review
- Call script review
- Confirmation checklist
- Follow-up date

### 4. Export (Not Send)
**Final step:**
- Download as text file
- User must copy/paste
- User manually hits Send in their email client

---

## Workflow Evidence: Session State

LIFT stores all workflow state in Streamlit session:

```python
st.session_state["consent_synthetic_data"]  # User acknowledged synthetic data
st.session_state["consent_no_sensitive_data"]  # User confirmed no sensitive data
st.session_state["consent_no_automation"]  # User understood no auto-sending
st.session_state["consent_human_approval"]  # User understood manual approval
st.session_state["privacy_session_only"]  # User opted for session-only history
st.session_state["privacy_include_notes"]  # User wants privacy notes in export
st.session_state["privacy_allow_website_checks"]  # User allows website checks
st.session_state["route_trace"]  # AI routing decision + reason
st.session_state["tool_trace"]  # Tool execution metadata
st.session_state["tool_result"]  # Full tool result (gaps, plans, etc.)
st.session_state["final_text"]  # Formatted report
st.session_state["generated_at"]  # Timestamp
```

---

## Acceptance Criteria Evidence

### ✅ App runs locally with `streamlit run app.py`
- Tested: Yes
- Works: Yes
- Demo mode works without API key: Yes

### ✅ App works even if no API key is present
- Uses demo output: Yes
- Shows labeled "DEMO FALLBACK": Yes
- Still generates resources, outreach, tracker: Yes

### ✅ Generate is blocked until required consent boxes are checked
- Consent section renders first: Yes
- Form hidden until all 4 checked: Yes
- Warning shows if unchecked: Yes

### ✅ App includes visible Agent Decision Trace
- Route decision displayed: Yes
- Reason shown: Yes
- Confidence level shown: Yes
- Evidence list shown: Yes

### ✅ App includes basic provider check tool
- MCP-style public HTTP check exists: Yes
- Function signature documented: Yes
- Input/output structure clear: Yes
- External data trace visible: Yes

### ✅ App generates warm outreach drafts for selected providers
- Provider selection UI: Yes
- Per-provider subject line: Yes
- Per-provider email draft: Yes
- Per-provider call script: Yes
- Confirmation checklist: Yes
- Follow-up date picker: Yes

### ✅ App includes follow-up tracker
- Table display: Yes
- Provider name, category, status shown: Yes
- CSV export button: Yes

### ✅ README explains the project clearly
- Overview section: Yes
- What it does/doesn't do: Yes
- Setup instructions: Yes
- Agentic workflow diagram: Yes
- MCP tool explanation: Yes
- Privacy limits documented: Yes

### ✅ `.env` remains ignored and is not committed
- .gitignore configured: Yes
- API key read from st.secrets or os.getenv: Yes
- No hardcoded keys: Yes

---

## Limitations & Future Work

### Current Limitations

1. **No real web scraping** – MCP tool uses demo data
2. **No email sending** – User must manually send
3. **No provider database sync** – All data is synthetic
4. **No authentication** – Anyone can access
5. **No audit logging** – No compliance records

### Future Enhancements

1. Real HTTP-based provider verification
2. OAuth2 login + role-based access control
3. Audit log for compliance
4. Email/SMS integration (with extra consent)
5. Integration with real resource databases
6. AI-powered barrier summarization
7. Provider feedback loop

---

## Conclusion

LIFT Agent successfully demonstrates:

✅ **Real agentic workflow** – Not just text generation  
✅ **Model-callable tools** – Real function calls via OpenAI tools API  
✅ **Human approval layers** – Consent + provider selection + review  
✅ **Honest about limitations** – Synthetic data, no auto-sending, demo mode when no API key  
✅ **Clear routing logic** – AI explains its decision  
✅ **MCP-style structure** – Tool input/output documented  
✅ **Privacy-first design** – Consent up front, session-only option  

This is a draft tool that teaches AI responsible development.
