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
`analyze_project_request`

Location:
`p3_tools.py`

Purpose:
This is the project tool that the model requests before writing the final output.
