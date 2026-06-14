# Project 3 Final AI Application Shell

## Working Title

Replace this with the final Project 3 title.

Example:
**Project 3 Final: Adaptive AI Decision Support Agent**

## Purpose

This project is a final AI application shell built from the lessons learned in Project 1 and Project 2.

Project 1 focused on foundational AI application concepts such as prompts, grounding, role-based instructions, structured outputs, constraints, and evaluation.

Project 2, TrendLens AI, improved that foundation by adding a Streamlit interface, deployment readiness, authentication/demo mode, saved outputs, monitoring logic, feedback logging, evaluation records, and a real model-callable tool workflow.

Project 3 should combine those lessons into a cleaner final product:
- Clear user problem.
- Real LLM decision point.
- Real tool/function call.
- Honest routing explanation.
- Evaluation records.
- Build log.
- Security/secrets handling.
- Deployed Streamlit app.
- README that does not overclaim.

## Key Project 3 Lesson Applied

The main Project 2 feedback was that changing prompt text is not the same as true model routing. For Project 3, this shell includes:

1. An LLM router that chooses a route based on the user request.
2. A route-to-model selection function.
3. A model-callable tool named `analyze_project_request`.
4. A tool trace shown in the app.
5. An evaluation record saved to `Tests/eval_results.md`.

## Suggested File Structure

```text
Project3_Final_Shell/
├── .streamlit/
│   └── config.toml
├── assets/
│   └── README_assets.md
├── Data/
│   └── sample_input.md
├── Docs/
│   └── project3_design_notes.md
├── Evidence/
│   └── test_run_notes.md
├── Monitoring/
│   └── example_monitoring_log.md
├── Outputs/
│   └── example_output.md
├── Prompts/
│   ├── router_prompt.md
│   └── system_prompt.md
├── scripts/
│   └── create_project_snapshot.py
├── Tests/
│   ├── eval_results.md
│   └── test_smoke.py
├── app.py
├── auth.py
├── p3_tools.py
├── monitoring.py
├── scheduler_worker.py
├── security_utils.py
├── ui_components.py
├── BUILD_LOG.md
├── API_PROMPT_LOG.md
├── README.md
├── requirements.txt
└── .gitignore
```

## Local Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Secrets

Do not commit API keys.

Use one of these:

### Local `.env`

```text
OPENAI_API_KEY=your_key_here
```

### Streamlit secrets

Create:

```text
.streamlit/secrets.toml
```

Add:

```toml
OPENAI_API_KEY = "your_key_here"
```

Do not push `secrets.toml`.

## Environment Variables

Optional:

```text
P3_DEFAULT_MODEL=gpt-4o-mini
P3_FAST_MODEL=gpt-4o-mini
P3_DEEP_MODEL=gpt-4o
P3_SOURCE_COMPARISON_MODEL=gpt-4o
P3_MONITORING_MODEL=gpt-4o-mini
P3_AUTH_REQUIRED=false
```

If you get model access errors, set all model variables to:

```text
gpt-4o-mini
```

## Final Submission Checklist

- [ ] App runs locally with `streamlit run app.py`.
- [ ] App deploys on Streamlit Cloud.
- [ ] API key is stored in Streamlit secrets, not GitHub.
- [ ] `README.md` explains the project honestly.
- [ ] `BUILD_LOG.md` documents major changes.
- [ ] `Tests/eval_results.md` includes expected vs actual test runs.
- [ ] Evidence folder contains screenshots or notes.
- [ ] App shows LLM route decision and tool trace.
- [ ] Final reflection explains how Project 1 and Project 2 feedback shaped Project 3.
