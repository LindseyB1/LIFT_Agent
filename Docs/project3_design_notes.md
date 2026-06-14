# Project 3 Design Notes

## Problem

Replace this with the final user problem.

Good format:
This app helps [user type] do [task] by using [AI workflow/tool] to produce [specific output].

## Target User

Replace this with the final target user.

Examples:
- Student
- Analyst
- Small business owner
- Emergency management user
- Cybersecurity learner
- Community resource coordinator

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

Project 3 adds an LLM routing decision before generation and records the route, model selected, tool call, and evaluation result.
