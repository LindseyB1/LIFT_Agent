# LIFT Sample Inputs

Use these examples to test the deployed Streamlit app and local automated tests.

## Eval Case 1: Food Access With Schedule Barrier

User need:
`I need a food pantry near Grand Rapids, but I work third shift and have limited transportation. I am not sure what documents I have.`

Expected route:
`gap_analysis`

Expected useful output:
- Matched food/basic-needs resources or clearly labeled fallback resources.
- Transportation, hours, and documentation barriers.
- Three contingency plans.
- Outreach draft that asks for eligibility, hours, intake method, and language support if needed.
- Tracker rows with next action and follow-up status.
- Curated corpus citations for verification, outreach, and tracking guidance.

## Eval Case 2: Provider Verification

User need:
`Can you help me verify whether this housing resource is still active and what intake documents they require?`

Expected route:
`validation_review`

Expected useful output:
- No claim that the provider is verified unless the website check succeeds.
- Verification checklist.
- Warm outreach draft limited to fit and availability questions.
- Clear note that the user must confirm details directly.

## Eval Case 3: Repeated System Gap

User need:
`I called three places and each one said they do not serve my ZIP code. I need help explaining the gap and tracking what to try next.`

Expected route:
`system_gap_brief`

Expected useful output:
- System gap summary.
- Tracker rows or next-step columns.
- Backup search strategy.
- No generic advice that ignores the repeated eligibility failure.
