# LIFT Evaluation Results

Date: 2026-06-21

## Automated Test Run

Command:
`$env:PYTHONDONTWRITEBYTECODE='1'; python Tests\test_smoke.py`

Result:
PASS

Output:
```text
...
----------------------------------------------------------------------
Ran 3 tests in 3.003s

OK
```

Coverage:
- Imports core modules.
- Confirms the local curated corpus retrieval returns citation IDs.
- Confirms the demo tool workflow returns matched resources, three contingency plans, tracker rows, retrieval trace, and citations.

Command:
`python -m pytest Tests/test_smoke.py -v`

Result:
NOT RUN IN THIS LOCAL ENVIRONMENT

Output:
```text
C:\Users\britn\AppData\Local\Programs\Python\Python313\python.exe: No module named pytest
```

Reason:
`pytest` is listed in `requirements.txt`, but it is not installed in this local Python environment. The test file also supports direct `unittest` execution, which passed.

## Qualitative Eval Case 1: Food Access With Schedule Barrier

Input:
`I need a food pantry near Grand Rapids, but I work third shift and have limited transportation. I am not sure what documents I have.`

Expected route:
`gap_analysis`

Expected behavior:
- Identify transportation, hours, and documentation barriers.
- Use public search rows or clearly labeled fallback data.
- Retrieve local corpus guidance on barriers, verification, outreach, and tracking.
- Generate three contingency plans.
- Generate tracker rows.

Actual local automated result:
PASS through `test_demo_tool_result_is_structured_and_cited`.

Failure analysis:
The automated test does not verify live OpenAI prose quality or Streamlit rendering. It verifies the deterministic core workflow that supports demo mode and the model-callable tool path.

## Qualitative Eval Case 2: Provider Verification

Input:
`Can you help me verify whether this housing resource is still active and what intake documents they require?`

Expected route:
`validation_review`

Expected behavior:
- Do not claim the provider is verified unless the basic public website check succeeds.
- Ask for current phone, website, hours, eligibility, intake process, and documents.
- Keep outreach as a draft requiring human approval.

Status:
Manual app eval still needed after deployment secrets are confirmed.

Failure analysis:
The provider website check depends on public URL availability and network access. The app now honors the privacy toggle before running checks.

## Qualitative Eval Case 3: Repeated System Gap

Input:
`I called three places and each one said they do not serve my ZIP code. I need help explaining the gap and tracking what to try next.`

Expected route:
`system_gap_brief`

Expected behavior:
- Summarize repeated ZIP-code eligibility failure as a system gap.
- Produce tracking columns and next steps.
- Avoid generic advice that ignores the repeated failure.

Status:
Prompt-level eval case documented; should be manually run against the deployed app.

## Model Comparison Status

OpenAI:
Implemented through `OPENAI_API_KEY` and `gpt-4o-mini` default.

Second provider:
Not run locally because no second provider credential is configured in this workspace. The comparison prompt and scoring rubric are documented in `Prompts/model_comparison_prompt.md`.

Honest limitation:
The deterministic demo fallback is useful for local testing, but it is not a true second model provider.
