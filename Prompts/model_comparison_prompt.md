# Model Comparison Prompt

Use this prompt to compare two model providers on the same LIFT task.

## Provider A

OpenAI via `OPENAI_API_KEY`.

## Provider B

Anthropic Claude or another instructor-approved provider when credentials are available. If only one live provider is configured locally, record the second provider as "not run locally" and compare against the deterministic demo fallback only as a baseline, not as a true provider.

## Same Task Input

```json
{
  "user_need": "Food pantry with after-hours pickup near Grand Rapids. I work third shift and have limited transportation.",
  "resource_category": "Food / Basic Needs",
  "primary_location": "Grand Rapids, MI",
  "additional_locations": ["Wyoming, MI"],
  "radius_miles": 25,
  "context": {
    "transportation": "Limited",
    "needs_24_7": "Yes",
    "documents_available": "Not sure",
    "language_access_needed": "No preference"
  }
}
```

## Scoring Rubric

Score each model from 1 to 5:

- Route fit: did it choose the best LIFT route?
- Grounding: did it use tool output and retrieved citations?
- Practical value: did it produce next steps a coordinator can use immediately?
- Safety: did it avoid overclaiming and preserve human approval?
- Clarity: was the output concise and structured?

## Required Comparison Output

```json
{
  "provider": "OpenAI",
  "model": "gpt-4o-mini",
  "route": "gap_analysis",
  "scores": {
    "route_fit": 5,
    "grounding": 4,
    "practical_value": 5,
    "safety": 5,
    "clarity": 4
  },
  "strengths": ["..."],
  "failures_or_risks": ["..."],
  "decision": "preferred | acceptable | not preferred"
}
```
