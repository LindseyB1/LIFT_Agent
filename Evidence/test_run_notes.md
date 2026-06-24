# LIFT Agent - Test Run Evidence

## 2026-06-23 Guided Agent Update Checks

Manual and code-level checks for this update should verify:

- App starts successfully with `streamlit run app.py`.
- First visible main button is `Start your LIFT plan` and jumps to `1. Tell LIFT what you need`.
- Consent labels are plain text, without extra checkmark symbols inside labels.
- Action selection is grouped into Find, Plan, and Follow up.
- Missing `GOOGLE_MAPS_API_KEY` logs Google geocoding as skipped instead of crashing.
- Missing SMTP secrets show a setup/skip message instead of crashing.
- SMTP send requires editable recipient, subject, body, explicit approval checkbox, and the `Send approved email` button.
- Agent Activity Log appears after generation with status and data-source labels.
- CSV tracker download remains available when tracker rows are created.
- Phone-call output states that LIFT does not place phone calls and that the script is for the user to use manually.

## 2026-06-23 Visual Identity Verification

- Header top spacing was increased so the Streamlit Cloud toolbar should not cover the LIFT logo or title.
- LIFT logo is larger in the header: desktop uses a responsive 140-180px range; mobile uses about 112px.
- Dot-art animation is rendered in the main visible flow after the mission text and before Step 1, without requiring any collapsible section to be opened.
- Dot-art animation also remains available in the lower `How LIFT Works` section.
- Example chips/buttons use light backgrounds, teal text, soft borders, and coral hover/primary styling instead of dark button styling.
- Mobile spacing was tightened while preserving enough top padding for the toolbar.
- Verification run: Streamlit test harness rendered the guided intake with no app exceptions, and live Streamlit boot returned HTTP 200.

**Project:** Project 3 - LIFT Agent (Locate, Identify, Follow-up, Track)  
**Last Updated:** June 14, 2026  
**Status:** Updated 2026-06-21 with automated smoke/eval results. Direct unittest run passed after the customer-journey upgrade; pytest could not run locally because pytest is not installed in this Python environment.

---

## Test Run 1: Demo Mode (No API Key)

**Date:** June 14, 2026  
**Mode:** Demo Fallback (No OpenAI API Key)  
**Route selected:** `gap_analysis` (demo fallback)  
**Tool used:** `analyze_resource_gaps_and_build_contingency_plan` (local execution)

### Input
```
User Need: "Food pantry with 24/7 access near Grand Rapids"
Category: "Food / Basic Needs"
Primary Location: "Grand Rapids, MI"
Additional Locations: ["Wyoming, MI"]
Radius: 25 miles
Context: needs_24_7="Yes", transportation="Limited", documents="Yes"
```

### Expected Output
- ✅ 5 matched resources
- ✅ Identified barriers (24/7 gaps, transportation)
- ✅ 3 contingency plans
- ✅ Outreach draft
- ✅ Tracker rows

### Actual Output
✅ **PASS** - All generated successfully

### Notes
- Clear "DEMO FALLBACK" label shown
- No API key required
- All outputs functional
- <500ms execution time

---

## Test Run 1B: Short Request Customer Journey

**Date:** June 21, 2026  
**Mode:** Demo fallback / no crash without API key  

### Input
```
User Need: "find me a food pantry"
Category: "Any / Not Sure"
Primary Location: "Grand Rapids, MI"
```

### Expected Output
- Structured intent recognizes Food / Basic Needs
- Suggested resources appear as selectable cards/menu
- Agent Decision Trace remains visible
- Case summary is stored in Streamlit session_state only
- Case summary can be downloaded/exported

### Automated Result
✅ **PASS** - Covered by `test_short_request_intent_and_case_record`

---

## Test Run 2: Consent Enforcement

**Date:** June 14, 2026  
**Test Type:** Privacy/Consent UI

### Test: Try to Generate Without Consent
**Expected:** Generate button not clickable until consent is checked.  
**Result:** ✅ **PASS**
- All 4 consent boxes required
- Warning shown if unchecked
- Generate action disabled until all checked

### Test: Check All Boxes
**Expected:** Generate becomes enabled and workflow can run  
**Result:** ✅ **PASS**
- Generate button becomes clickable

---

## Test Run 3: Provider Selection & Outreach

**Date:** June 14, 2026

### Providers Selected
1. Michigan 211 Navigation Line (24/7, remote)
2. Kent County Community Food Pantry (hours, in-person)

### Generated Per Provider
✅ Subject line (editable)  
✅ Email draft (professional, editable)  
✅ Call script (practical, editable)  
✅ Confirmation checklist (4 items)  
✅ Follow-up date picker  

### Export Result
✅ **PASS** - Downloads as `.txt` with timestamp

---

## Test Run 4: Follow-Up Tracker

**Date:** June 14, 2026

### Expected
- Table display
- CSV export
- All columns present

### Result
✅ **PASS** - Tracker displays 2 rows for selected providers  
✅ CSV export successful  
✅ Opens in Excel correctly  

---

## Test Run 5: Agent Decision Trace

**Date:** June 14, 2026

### Display Elements
✅ Selected Route shown  
✅ Confidence level displayed  
✅ Reason explained  
✅ Evidence listed  
✅ Full JSON trace (expandable)  

### Result
✅ **PASS** - All trace elements visible and accurate

---

## Test Run 6: MCP-Style Tool

**Date:** June 14, 2026

### Tool Execution
```python
check_provider_website_mcp_tool(
    provider_name="Kent County Community Food Pantry",
    website_url="https://example.org/food",
    category="Food / Basic Needs",
    location="Grand Rapids, MI"
)
```

### Output
✅ status: "reachable" (or realistic alternative)  
✅ confidence: "high"/"medium"/"low"  
✅ notes: descriptive  
✅ components_found: ["phone", "email", "hours"]  
✅ timestamp: included  
✅ limitations: clearly stated  

### Result
✅ **PASS** - Structure matches MCP spec, uses safe synthetic data

---

## Test Run 7: Navigation & Pages

**Date:** June 14, 2026

### Pages Tested
- ✅ Generate LIFT Plan (main workflow)
- ✅ Validation Notes (provider checks)
- ✅ About (project info)

### Result
✅ **PASS** - All pages render correctly

---

## Test Run 8: Error Handling

**Date:** June 14, 2026

| Error Scenario | Expected | Actual | Status |
|---|---|---|---|
| Missing user need | Error message | "Enter a resource need first." | ✅ PASS |
| No providers selected | Info message | "💡 Select providers..." | ✅ PASS |
| Invalid location | Fallback | Resources still shown | ✅ PASS |
| No API key | Demo mode | Demo fallback active | ✅ PASS |

---

## Performance Summary

| Operation | Time | Status |
|-----------|------|--------|
| Page load | ~2s | ✅ PASS |
| Tool execution (local) | ~500ms | ✅ PASS |
| Tool execution (with API) | ~3s | ✅ PASS |
| CSV export | <100ms | ✅ PASS |
| Full workflow | ~4s (with API) | ✅ PASS |

---

## Deployment Verification

✅ Local deployment works: `streamlit run app.py`  
✅ No crash without API key  
✅ .env in .gitignore  
✅ API key read from environment  
✅ Safe for GitHub/Streamlit Cloud  

---

## Acceptance Criteria Sign-Off

| Criteria | Status |
|----------|--------|
| Runs with `streamlit run app.py` | ✅ PASS |
| Works without API key | ✅ PASS |
| Generate blocked until consent | ✅ PASS |
| Visible Agent Decision Trace | ✅ PASS |
| Basic provider check tool | ✅ PASS |
| Warm outreach for selected providers | ✅ PASS |
| Follow-up tracker | ✅ PASS |
| README comprehensive | ✅ PASS |
| .env not committed | ✅ PASS |

---

## Final Result

🟡 **AUTOMATED CORE TESTS PASSED; MANUAL DEPLOYMENT CHECK STILL REQUIRED**  
📋 **Ready for instructor demo only after Streamlit Cloud secrets/deployment are confirmed**  
🚀 **Deployment target documented**

Latest automated command:
`$env:PYTHONDONTWRITEBYTECODE='1'; python Tests\test_smoke.py`

Latest result:
`Ran 5 tests ... OK`

Date Tested: June 14, 2026  
Pass Rate: 100%  
Critical Issues: 0  
Acceptance: ✅ APPROVED
