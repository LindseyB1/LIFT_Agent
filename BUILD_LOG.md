# Build Log

## Project 3: LIFT Agent

LIFT means Locate, Identify, Follow-up, Track. The product goal is to help a resource navigator or support staff member turn a messy community-support need into a grounded provider search, barrier review, outreach draft, and follow-up tracker.

## Iteration 1: Project Shell

Purpose:
Create a Streamlit app framework with prompts, tests, docs, and deployment notes.

Decision:
Start from a broad Project 3 shell, then specialize it into a disciplinary resource-navigation app.

Risk found:
Some early files still described a generic source-comparison assistant instead of LIFT.

## Iteration 2: LIFT Workflow

Changed:
- Main app became a single Streamlit workflow in `app.py`.
- Added public OpenStreetMap Nominatim search as the external grounding layer.
- Added demo fallback rows so the app still runs without an API key.
- Added OpenAI route selection and a model-callable function tool.
- Added provider website checks using safe public HTTP requests only.

Decision:
Keep the app honest: public search results are leads, not verified referrals.

## Iteration 3: UI And Human Approval

Changed:
- Added brand assets and animation.
- Added consent checkboxes.
- Added provider selection before outreach drafts.
- Added tracker CSV export and outreach draft text export.

Decision:
The user remains the approval layer. The app does not send email, call providers, monitor phones, or access voicemail.

## Iteration 4: Stabilization Review

Issues found:
- Consent was referenced before it was defined in `render_generate_page()`.
- Consent rendering lived inside `get_openai_client()`, which mixed UI control with API setup.
- `pandas` was imported but missing from `requirements.txt`.
- The snapshot script could include `.env` or generated files.
- Router prompt and sample input still reflected the older generic shell.
- Tests were only import-level smoke tests.

Changed:
- Moved consent rendering into the generate page before the form action.
- Kept `get_openai_client()` focused on API client creation.
- Added sensitive-marker warnings through `security_utils.validate_user_input()`.
- Enforced the website-check privacy toggle.
- Added `pandas` to requirements.
- Hardened `scripts/create_project_snapshot.py` against secrets and generated artifacts.

## Iteration 5: RAG And Evaluation Evidence

Changed:
- Added `Data/lift_curated_corpus.md`.
- Added deterministic local retrieval with Markdown-section chunking.
- Added citation IDs such as `LIFT-CORPUS-1`.
- Added retrieval trace to the Agent Decision Trace.
- Updated prompts with role, constraints, refusal behavior, structured output, step-by-step pattern, and few-shot route examples.
- Expanded tests to check retrieval citations and structured tool output.

Decision:
Use a small curated corpus instead of pretending public search results are a complete human-services directory.

## Iteration 6: Instructor Feedback Customer Journey Upgrade

Issues addressed:
- The app had strong backend agent traces but still felt too much like a project report.
- Suggested resources were shown mostly as a dataframe instead of a simple selectable menu.
- There was not a clear session-only "case on record" summary.
- Short requests needed to visibly become structured intent.
- Provider website/status tool output needed to be visible in the resource journey.
- The hover animation moved too quickly.

Changed:
- Added structured intent interpretation for short requests such as "find me a food pantry."
- Uses OpenAI interpretation when `OPENAI_API_KEY` is available and labeled demo fallback when it is not.
- Added `What LIFT understood` to show need type, search area, urgency, barriers/preferences, and missing information.
- Converted suggested resources into selectable cards while preserving the detailed dataframe in an expander.
- Added provider-check result display in resource details.
- Added a session-only case record with selected resources, follow-up actions, provider checks, timestamp, and download.
- Slowed the LIFT animation frame delay from 65ms to 260ms.

Decision:
Keep MVP state in `st.session_state`; do not add login, database, compliance system, or account management.

## Multi-Model Plan

Current implementation:
- OpenAI integration is live when `OPENAI_API_KEY` is configured.
- Demo fallback is deterministic and labeled as a baseline, not a second provider.

## Iteration 7: Final Agentic Compliance Review

Issues addressed:
- The live OpenAI workflow exposed tools but forced the main resource-gap tool through `tool_choice`, which made the agentic decision evidence weaker than the rubric expects.
- The README did not give one compact final-submission map from rubric requirement to project evidence.

Changed:
- Updated `run_live_llm_tool_workflow()` to expose both tool schemas with `tool_choice="auto"`.
- Added a short tool-call loop that executes model-requested `tool_calls`, returns tool messages, and lets the model either call another tool or finish.
- Added `tools_requested_by_model` to the runtime tool trace so the app can show which tools the model chose.
- Added a final submission checklist in `README.md`.

Decision:
Keep deterministic local fallback for no-key environments, but label it honestly. Live agentic evidence depends on `OPENAI_API_KEY` being configured so the LLM can choose tools.

Planned comparison:
- Use `Prompts/model_comparison_prompt.md` to run the same task through OpenAI and a second provider when credentials are available.
- Record scores in `Tests/eval_results.md`.

## Test Commands

Preferred:
`python -m pytest Tests/test_smoke.py -v`

Fallback without pytest:
`python Tests/test_smoke.py`

Latest direct test run:
`$env:PYTHONDONTWRITEBYTECODE='1'; python Tests\test_smoke.py`

Result:
5 tests passed.

## Deployment

Configured deployment target:
Streamlit Cloud app linked in `README.md`.

Instructor requirement:
The app must be public, operational, and connected to the GitHub repo. Environment secrets should be configured in Streamlit Cloud, not committed.
