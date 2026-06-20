# Project 3 Design Notes

## Problem

People who are trying to find community support often get stuck with scattered provider information, unclear eligibility rules, limited hours, transportation barriers, and outdated contact details. LIFT Agent helps turn a resource need into a structured provider search, gap review, outreach draft, and follow-up tracker while keeping human approval in control.

## Target User

- Community resource coordinator
- Student support staff member
- Military family readiness or veteran support volunteer
- Case-navigation learner practicing responsible AI workflows

## Lessons From Project 1

- Clear system prompt matters.
- Grounded outputs are stronger than generic outputs.
- Structured outputs are easier to evaluate.
- Constraints reduce hallucination.
- Evaluation should be planned early.

## Lessons From Project 2

- UI polish matters, but the workflow must be real.
- Tool calls need to be requested by the model, not only called by Python.
- Routing must be described honestly.
- Saved outputs, eval logs, and build logs help prove work.
- Deployment should be tested and documented.

## Project 3 Improvement

Project 3 adds an LLM routing decision before generation, a real external public resource search, a model-callable gap-analysis tool, a basic public provider website check, and visible trace records that show route selection, tool execution, and grounding source.
