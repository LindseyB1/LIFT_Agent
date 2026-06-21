# API and Prompt Log

Use this file to document important prompt and model changes.

## Router Prompt

Location:
`Prompts/router_prompt.md`

Purpose:
The router prompt asks the model to choose the best analysis route before generation.

## System Prompt

Location:
`Prompts/system_prompt.md`

Purpose:
The system prompt defines the assistant role, safety rules, grounding rules, and output expectations.

## Tool Use

Primary model-callable tool:
`analyze_resource_gaps_and_build_contingency_plan`

Location:
`app.py`

Purpose:
This is the project tool that the OpenAI model requests before writing the final output. It receives the user need, category, location/radius, context, selected outputs, public external search rows, and retrieved local corpus guidance. It returns structured matched resources, barriers, contingency plans, outreach draft, tracker rows, system gap notes, and citation IDs.

Supporting local analysis tool:
`analyze_project_request`

Location:
`p3_tools.py`

Purpose:
This remains available as a transparent text-analysis helper for keyword, urgency, and information-gap analysis.

## RAG Prompting

Location:
`Data/lift_curated_corpus.md`

Chunking:
The app chunks the local corpus by level-2 Markdown headings. Each section becomes one citation-ready chunk, such as `LIFT-CORPUS-2`.

Prompt use:
Retrieved chunks are stored in `context["retrieval_trace"]`, passed into the tool result, shown in the Agent Decision Trace, and cited in the generated report.

## Multi-Model / Routing Prompt

Location:
`Prompts/model_comparison_prompt.md`

Purpose:
Documents the same-task comparison rubric for OpenAI and a second provider when credentials are available. The deterministic demo fallback is treated as a baseline only, not as a true second provider.
