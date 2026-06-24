# LIFT Agent - Agentic Workflow Evidence

## Current Human-Supervised Agent Loop

LIFT Agent is a human-supervised autonomous resource navigation agent. The current app loop is:

```text
guided user intake -> selected agent actions -> public/external tool calls -> structured outputs -> human review -> optional approved SMTP send -> audit log and downloads
```

The operational loop is:

```text
Observe -> Reason -> Act -> Log
```

- Observe: collect need, search area, radius, transportation limits, preferred access, optional contact preferences, optional upload/link references, fit context, consent, and selected actions.
- Reason: infer resource category, urgency, barriers, fallback needs, and provider confidence.
- Act: run public search, provider website checks, optional Google Maps geocoding/map links, outreach draft generation, call script generation, tracker row creation, CSV export, and approved SMTP sending.
- Log: write each action to the Agent Activity Log with status, data source, explanation, and whether human approval was required.

The app does not place phone calls. Phone calls remain a manual user action; LIFT prepares the call plan, call script, checklist, and tracker row.

## Current Tool-Style Functions

- `search_public_resources()` searches public provider/resource information and labels fallback data when external search is unavailable.
- `check_provider_website()` performs basic public website checks through the existing MCP-style HTTP checker.
- `geocode_location_google()` geocodes Step 2 search-area locations when a Google Maps key is configured.
- `geocode_provider_locations()` uses `GOOGLE_MAPS_API_KEY` from Streamlit secrets or environment variables when configured.
- `build_google_maps_link()` creates provider map links from coordinates or location text.
- `render_google_map()` prepares mapped provider rows and Google Maps links when coordinates are available.
- `render_google_map_or_pydeck_map()` preserves the map-render helper expected by the app/tests.
- `generate_outreach_email()` creates a reviewed, editable outreach draft.
- `generate_call_script()` creates a manual phone-call script for the user.
- `send_email_smtp()` sends only approved email through SMTP credentials from secrets or environment variables.
- `create_tracker_rows()` creates follow-up tracker rows for provider options.
- `export_tracker_csv()` creates tracker CSV data for download.
- `write_agent_audit_log()` stores the Agent Activity Log in Streamlit session state for display and CSV export.

## Real-World Integrations

- Public resource search: OpenStreetMap Nominatim public API.
- Provider website check: public HTTP request only; no login, scripts, form submission, or restricted access.
- Google Maps/geocoding: optional Google Maps Geocoding API using `GOOGLE_MAPS_API_KEY`.
- Email: optional SMTP using `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, and `SMTP_FROM`.

Secrets are never hardcoded and should not be committed.

## Example Agent Activity Log

| timestamp | action | status | data_source | message |
| --- | --- | --- | --- | --- |
| 2026-06-23 10:15:02 | User need received | completed | local/session data | The guided intake was submitted. |
| 2026-06-23 10:15:02 | Primary location received | completed | local/session data | Primary search location was received from Step 2. |
| 2026-06-23 10:15:02 | Additional locations received/skipped | completed | local/session data | 1 additional location received. |
| 2026-06-23 10:15:02 | Search radius received | completed | local/session data | Search radius received: 25 miles. |
| 2026-06-23 10:15:02 | Transportation limits received | completed | local/session data | Transportation limit received. |
| 2026-06-23 10:15:02 | Preferred access received | completed | local/session data | Preferred access received. |
| 2026-06-23 10:15:02 | Optional contact info received | skipped | local/session data | No optional contact preferences were provided. |
| 2026-06-23 10:15:02 | File upload received | skipped | local/session data | No optional files were uploaded. |
| 2026-06-23 10:15:02 | Link reference received | skipped | local/session data | No optional links were provided. |
| 2026-06-23 10:15:03 | Public resource search started | completed | real external API/tool data | Searching public provider information with OpenStreetMap Nominatim. |
| 2026-06-23 10:15:05 | Provider candidates found | completed | real external API/tool data | 5 provider candidate rows prepared. |
| 2026-06-23 10:15:07 | Provider website checked | completed | real external API/tool data | Provider website status returned. |
| 2026-06-23 10:15:08 | Google Maps/geocoding | skipped | local/session data | GOOGLE_MAPS_API_KEY is not configured. Typed location text and public-search coordinates are used. |
| 2026-06-23 10:15:08 | Provider map links created | completed | local/session data | Existing provider coordinates and location text were used for map links. |
| 2026-06-23 10:15:09 | Outreach email draft created | completed | local/session data | Editable outreach draft prepared for human review. |
| 2026-06-23 10:15:09 | Tracker rows created | completed | local/session data | 5 tracker rows prepared. |
| 2026-06-23 10:15:09 | SMTP email sending | skipped | local/session data | SMTP email is only sent from the review panel after explicit approval. |

The live app also includes a `human_approval_required` column. Outreach email draft generation and SMTP email sending are marked as requiring approval.

## Example Tracker Row

```json
{
  "Case ID": "LIFT-20260623-001",
  "Need Category": "Food / Basic Needs",
  "User Need": "Food pantry near me",
  "Resource Name": "Example Community Food Pantry",
  "Contact Method": "Phone / Email / Website",
  "Status": "Pending Outreach",
  "Progress %": 10,
  "Next Action": "Verify eligibility, hours, availability, and intake process.",
  "Outcome": "",
  "Notes": "Public search result; confirm before relying on this provider.",
  "user_preferred_contact_method": "Not sure",
  "user_outreach_language": "",
  "user_email_provided": "no",
  "supporting_files_count": 0,
  "supporting_links_count": 0,
  "notes_from_user_context": ""
}
```

## LIFT Character Guides and Optional Context

Step 4 includes five guide cards:

- Lia is the main guide and selects the full plan.
- Scout maps to Locate actions: public search, provider website checks, and Google map.
- Ivy maps to Identify actions: resource fit summary, barriers/gaps, and backup options.
- Ember maps to Follow-up actions: email drafts and call scripts.
- Tally maps to Track actions: tracker rows and CSV download.

The optional context card accepts optional email, preferred contact method, outreach language, best contact time, user notes, uploads, and links. Email is not required. Uploaded files are session-only unless storage is added later; current output shows names/types and does not claim full file or photo understanding. Google Drive or Google Docs links are reference links only unless a future authenticated Google Drive integration is added.

## Example Provider Confidence Label

```json
{
  "provider": "Example Community Food Pantry",
  "confidence_label": "Medium confidence",
  "confidence_reason": "Provider appears relevant, but hours, eligibility, or availability need confirmation.",
  "next_best_action": "Call to confirm walk-in hours and current availability."
}
```

Confidence labels are intentionally conservative:

- High confidence: website reachable, location available, and category appears to match the need.
- Medium confidence: provider appears relevant, but hours, eligibility, or availability need confirmation.
- Low confidence: limited public information, missing address, unreachable website, or fallback/example data used.

## SMTP Approval Flow

1. LIFT generates an outreach email draft.
2. The user reviews and edits recipient, subject, and body.
3. The user checks: `I reviewed and approve this email to be sent.`
4. The user clicks `Send approved email`.
5. `send_email_smtp()` checks SMTP secrets/environment variables.
6. The Agent Activity Log records `completed`, `skipped`, or `failed`.

Missing SMTP credentials produce a setup/skip message and do not crash the app.

## Google Maps / Geocoding Flow

1. LIFT uses provider addresses or public-search location strings.
2. Step 2 search area geocoding and provider geocoding use `GOOGLE_MAPS_API_KEY` from `st.secrets` or environment variables only.
3. If `GOOGLE_MAPS_API_KEY` is configured, `geocode_location_google()` and `geocode_provider_locations()` request coordinates from Google Maps.
4. Mapped rows include latitude, longitude, geocoding status, and Google Maps links when available.
5. If the key is missing or an address is incomplete, the action is logged as skipped or failed, and available location text remains visible.

## Failure and Fallback Handling

Fallback is labeled at the action level:

- `External resource search unavailable. Showing clearly labeled fallback resource examples.`
- `GOOGLE_MAPS_API_KEY is not configured. Google geocoding skipped.`
- `SMTP email sending skipped because approval was not provided.`
- `SMTP email sending skipped because credentials are missing.`
- `Provider website check failed for this provider; public contact details still need manual verification.`

## Screenshot Placeholders

Screenshots were not regenerated in this terminal session. Suggested screenshots:

- Guided intake first screen with `Start your LIFT plan`
- Action selection cards/checkboxes
- Agent Activity Log
- Provider Options and Map View
- SMTP approval panel
- Tracker Rows and Downloads

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
│  Next Step: User manually sends or approves SMTP in-app    │
│  App Role: HUMAN-SUPERVISED OUTREACH SUPPORT                          │
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
- Human-supervised automation confirmation
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

### 4. Export or Approved SMTP Send
**Final step:**
- Download as text file
- User may manually copy/paste into their email client
- SMTP send requires configured credentials, an editable message, an approval checkbox, and the `Send approved email` button

### 5. Session Case Record
**MVP record handling:**
- Current case is stored in `st.session_state`
- Case summary includes user request, interpreted intent, suggested resources, selected resources, provider checks, follow-up actions, and timestamps
- No permanent database storage is created
- User can download/export the case summary

---

## Workflow Evidence: Session State

LIFT stores all workflow state in Streamlit session:

```python
st.session_state["consent_synthetic_data"]  # User acknowledged public external data or labeled fallback data
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
st.session_state["interpreted_intent"]  # Structured need/location/barrier interpretation
st.session_state["current_case_record"]  # Session-only MVP case summary
st.session_state["case_history"]  # User-saved case records for the current session
```

---

## Acceptance Criteria Evidence

### ✅ App imports and core workflow tests pass locally
- Tested: Yes
- Direct test command: `$env:PYTHONDONTWRITEBYTECODE='1'; python Tests\test_smoke.py`
- Result: PASS, 3 tests
- Demo mode core tool workflow works without API key: Yes

### ✅ App works even if no API key is present
- Uses labeled local routing fallback if no OpenAI API key is present: Yes
- Shows labeled "DEMO FALLBACK": Yes
- Still generates resources, outreach, tracker: Yes

### ✅ Generate is blocked until required consent boxes are checked
- Consent section renders before generation controls: Yes
- Generate action is disabled until all 4 boxes are checked: Yes
- Warning shows if unchecked: Yes

### ✅ App includes visible Agent Decision Trace
- Route decision displayed: Yes
- Reason shown: Yes
- Confidence level shown: Yes
- Evidence list shown: Yes
- Structured intent shown: Yes
- Tool and provider check traces visible: Yes

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

### ✅ App includes session-only case record
- User request and interpreted intent captured: Yes
- Suggested and selected resources captured: Yes
- Follow-up actions captured: Yes
- Download/export available: Yes
- No database or login required: Yes

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

1. **No real web scraping** – MCP-style provider check uses public HTTP requests but does not execute JavaScript, log in, or submit forms
2. **Human-supervised email sending only** – SMTP requires credentials and explicit approval; otherwise the user manually sends drafts
3. **No provider database sync** – Public search results are not a formal 211-style human-services directory
4. **No authentication** – Anyone can access
5. **Activity Log is not compliance-grade** – Agent Activity Log records action status, source, and approval flags, but it is not a compliance audit log

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
✅ **Honest about limitations** – Public search data requires verification, no auto-sending, demo routing mode when no API key  
✅ **Clear routing logic** – AI explains its decision  
✅ **MCP-style structure** – Tool input/output documented  
✅ **Privacy-first design** – Consent up front, session-only option  

This is a human-supervised agent that demonstrates responsible AI development.


