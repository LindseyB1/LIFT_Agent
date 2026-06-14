import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

from auth import render_auth_gate
from monitoring import compare_text_changes, save_monitoring_result
from p3_tools import analyze_project_request
from security_utils import validate_user_input
from ui_components import render_header, render_safety_notice, render_welcome_panel

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
    OPENAI_IMPORT_ERROR = ""
except Exception as error:
    OpenAI = None
    OPENAI_AVAILABLE = False
    OPENAI_IMPORT_ERROR = str(error)


APP_NAME = "Project 3 Final AI Agent"
APP_SUBTITLE = "A final AI application shell built from Project 1 and Project 2 lessons."

OUTPUTS_DIR = Path("Outputs")
TESTS_DIR = Path("Tests")
MONITORING_DIR = Path("Monitoring")

DEFAULT_MODEL = os.getenv("P3_DEFAULT_MODEL", "gpt-4o-mini")
FAST_MODEL = os.getenv("P3_FAST_MODEL", "gpt-4o-mini")
DEEP_MODEL = os.getenv("P3_DEEP_MODEL", "gpt-4o")
SOURCE_COMPARISON_MODEL = os.getenv("P3_SOURCE_COMPARISON_MODEL", "gpt-4o")
MONITORING_MODEL = os.getenv("P3_MONITORING_MODEL", "gpt-4o-mini")
EXECUTIVE_MODEL = os.getenv("P3_EXECUTIVE_MODEL", "gpt-4o-mini")
FALLBACK_MODEL = os.getenv("P3_FALLBACK_MODEL", "gpt-4o-mini")


ROUTE_MODEL_MAP = {
    "fast_summary": FAST_MODEL,
    "deep_analysis": DEEP_MODEL,
    "source_comparison": SOURCE_COMPARISON_MODEL,
    "monitoring_update": MONITORING_MODEL,
    "executive_brief": EXECUTIVE_MODEL,
    "fallback_review": FALLBACK_MODEL,
}


ANALYZE_PROJECT_REQUEST_TOOL = {
    "type": "function",
    "function": {
        "name": "analyze_project_request",
        "description": (
            "Analyze the user's Project 3 request before final output. Identify likely need, "
            "complexity, keywords, information gaps, recommended output elements, and limits."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_request": {
                    "type": "string",
                    "description": "The user's public or synthetic request text.",
                },
                "output_style": {
                    "type": "string",
                    "description": "The output style selected by the user.",
                },
                "project_goal": {
                    "type": "string",
                    "description": "The purpose or goal of the Project 3 app.",
                },
            },
            "required": ["user_request", "output_style", "project_goal"],
            "additionalProperties": False,
        },
    },
}


def initialize_session_state():
    defaults = {
        "latest_output": "",
        "latest_metadata": {},
        "latest_route_trace": {},
        "latest_tool_trace": {},
        "latest_eval_saved": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def ensure_project_folders():
    OUTPUTS_DIR.mkdir(exist_ok=True)
    TESTS_DIR.mkdir(exist_ok=True)
    MONITORING_DIR.mkdir(exist_ok=True)


def get_openai_api_key():
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", "")
        if api_key:
            return api_key
    except Exception:
        pass

    return os.getenv("OPENAI_API_KEY", "")


def get_openai_client():
    if not OPENAI_AVAILABLE:
        raise RuntimeError(
            f"The openai package is not available. Install it with: pip install openai. Details: {OPENAI_IMPORT_ERROR}"
        )

    api_key = get_openai_api_key()

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to Streamlit secrets or set it as a local environment variable."
        )

    return OpenAI(api_key=api_key)


def parse_json_safely(text):
    try:
        return json.loads(text)
    except Exception:
        pass

    # Handles occasional fenced JSON from the model.
    cleaned = str(text or "").strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except Exception:
        return {}


def llm_select_route(client, user_request, output_style, project_goal):
    """
    Real LLM routing step.

    This is intentionally separate from the final report call so Project 3 can document:
    - what route the LLM chose,
    - why it chose it,
    - which model the app dispatched to next.
    """
    route_prompt = f"""
You are the Project 3 routing assistant.

Choose one route for the user's request:

1. fast_summary
2. deep_analysis
3. source_comparison
4. monitoring_update
5. executive_brief
6. fallback_review

Return JSON only with:
- route
- reason
- confidence
- evidence

Project goal:
{project_goal}

Output style requested:
{output_style}

User request:
{user_request}
"""

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You choose the best route for an AI application. Return valid JSON only.",
            },
            {"role": "user", "content": route_prompt.strip()},
        ],
        temperature=0,
    )

    raw_content = response.choices[0].message.content or ""
    route_decision = parse_json_safely(raw_content)

    route = route_decision.get("route", "fallback_review")
    if route not in ROUTE_MODEL_MAP:
        route = "fallback_review"

    selected_model = ROUTE_MODEL_MAP[route]

    return {
        "routing_mode": "LLM route selection with model dispatch",
        "router_model": DEFAULT_MODEL,
        "selected_route": route,
        "selected_model": selected_model,
        "reason": route_decision.get("reason", "No reason returned."),
        "confidence": route_decision.get("confidence", "unknown"),
        "evidence": route_decision.get("evidence", []),
        "raw_router_response": raw_content,
    }


def build_generation_messages(user_request, output_style, project_goal, route_trace):
    system_message = f"""
You are {APP_NAME}.

You are a final Project 3 AI application assistant.

Required workflow:
1. Use the analyze_project_request function tool before writing the final output.
2. Use the tool result as the grounding layer.
3. Do not claim external verification unless a search tool was actually used.
4. Separate facts from assumptions.
5. Show uncertainty when information is incomplete.
6. Produce a clean structured output for the selected output style.
7. Do not include secrets, API keys, passwords, or sensitive data.
"""

    user_message = f"""
Project goal:
{project_goal}

Output style:
{output_style}

LLM routing decision:
{json.dumps(route_trace, indent=2)}

User request:
{user_request}

After the function tool returns its result, write the final answer.
"""

    return [
        {"role": "system", "content": system_message.strip()},
        {"role": "user", "content": user_message.strip()},
    ]


def run_llm_tool_workflow(user_request, output_style, project_goal):
    client = get_openai_client()

    route_trace = llm_select_route(
        client=client,
        user_request=user_request,
        output_style=output_style,
        project_goal=project_goal,
    )

    selected_model = route_trace["selected_model"]

    messages = build_generation_messages(
        user_request=user_request,
        output_style=output_style,
        project_goal=project_goal,
        route_trace=route_trace,
    )

    first_response = client.chat.completions.create(
        model=selected_model,
        messages=messages,
        tools=[ANALYZE_PROJECT_REQUEST_TOOL],
        tool_choice={
            "type": "function",
            "function": {"name": "analyze_project_request"},
        },
        temperature=0.2,
    )

    first_message = first_response.choices[0].message
    tool_calls = first_message.tool_calls or []

    if not tool_calls:
        raise RuntimeError(
            "The model did not request analyze_project_request. The output was not generated because model tool use is required."
        )

    messages.append(first_message.model_dump(exclude_none=True))

    tool_trace = {
        "generation_mode": "LLM routing plus model-callable tool workflow",
        "selected_route": route_trace["selected_route"],
        "selected_model": selected_model,
        "tool_requested_by_model": False,
        "tool_name": "",
        "tool_result_summary": {},
        "workflow_steps": [
            "The app asked the LLM router to choose a route.",
            "The app mapped the chosen route to a model.",
            "The app provided a function schema to the selected model.",
            "The model requested analyze_project_request.",
            "The app executed the local Python tool.",
            "The tool result was returned to the model.",
            "The model generated the final output using the tool result.",
        ],
    }

    for tool_call in tool_calls:
        tool_name = tool_call.function.name

        if tool_name != "analyze_project_request":
            raise RuntimeError(f"Unexpected tool requested by model: {tool_name}")

        try:
            arguments = json.loads(tool_call.function.arguments or "{}")
        except json.JSONDecodeError:
            arguments = {}

        tool_result = analyze_project_request(
            user_request=arguments.get("user_request", user_request),
            output_style=arguments.get("output_style", output_style),
            project_goal=arguments.get("project_goal", project_goal),
        )

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result, indent=2),
            }
        )

        tool_trace["tool_requested_by_model"] = True
        tool_trace["tool_name"] = "analyze_project_request"
        tool_trace["tool_result_summary"] = {
            "complexity": tool_result["complexity"],
            "word_count": tool_result["word_count"],
            "keywords": tool_result["keywords"],
            "recommended_output_elements": tool_result["recommended_output_elements"],
        }

    final_response = client.chat.completions.create(
        model=selected_model,
        messages=messages,
        temperature=0.3,
    )

    final_output = final_response.choices[0].message.content or ""

    if not final_output.strip():
        raise RuntimeError("The model returned an empty output.")

    return final_output, route_trace, tool_trace


def save_output(output_text, metadata):
    OUTPUTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUTS_DIR / f"project3_output_{timestamp}.md"

    record = f"""# Project 3 Output

## Metadata

```json
{json.dumps(metadata, indent=2)}
```

## Output

{output_text}
"""

    path.write_text(record, encoding="utf-8")
    return path


def save_eval_record(expected_output, actual_output, metadata, route_trace, tool_trace):
    TESTS_DIR.mkdir(exist_ok=True)
    path = TESTS_DIR / "eval_results.md"
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    record = f"""
## Evaluation Record

Date:
{created_at}

Test purpose:
Confirm Project 3 uses an LLM routing decision and a model-callable tool before generating the final output.

Expected output:
{expected_output.strip()}

Actual output:
{actual_output.strip()}

Metadata:
~~~json
{json.dumps(metadata, indent=2)}
~~~

LLM route trace:
~~~json
{json.dumps(route_trace, indent=2)}
~~~

Model tool trace:
~~~json
{json.dumps(tool_trace, indent=2)}
~~~

Result:
Successful if the route trace shows an LLM-selected route/model and the tool trace shows the model requested analyze_project_request.

---
"""

    with path.open("a", encoding="utf-8") as file:
        file.write(record)

    return path


def render_generate_tab():
    st.header("1. Define the Project 3 Task")

    project_goal = st.text_area(
        "Project goal",
        value=(
            "Help a user turn public or synthetic input into a structured, grounded decision-support output."
        ),
        height=100,
    )

    output_style = st.selectbox(
        "Output style",
        [
            "Concise summary",
            "Detailed analysis",
            "Source comparison",
            "Executive brief",
            "Monitoring update",
            "Action plan",
        ],
    )

    user_request = st.text_area(
        "User request / public or synthetic input",
        height=260,
        placeholder="Paste the request or safe public/synthetic information here.",
    )

    input_errors, input_warnings = validate_user_input(user_request)

    for warning in input_warnings:
        st.warning(warning)

    for error in input_errors:
        if user_request.strip():
            st.error(error)

    st.divider()

    st.header("2. Generate")

    if not OPENAI_AVAILABLE:
        st.error(
            f"The openai package is not installed. Install it with: pip install openai. Details: {OPENAI_IMPORT_ERROR}"
        )

    if not get_openai_api_key():
        st.warning(
            "OPENAI_API_KEY is missing. Add it to Streamlit secrets or a local .env/environment variable before generating."
        )

    generate_button = st.button("Generate Project 3 Output", type="primary", use_container_width=True)

    if generate_button:
        if not user_request.strip():
            st.error("Enter a request before generating.")
            st.stop()

        with st.spinner("Running LLM route selection and model-callable tool workflow..."):
            try:
                final_output, route_trace, tool_trace = run_llm_tool_workflow(
                    user_request=user_request,
                    output_style=output_style,
                    project_goal=project_goal,
                )

                metadata = {
                    "app_name": APP_NAME,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "project_goal": project_goal,
                    "output_style": output_style,
                    "generation_mode": "LLM routing plus model-callable tool workflow",
                    "selected_route": route_trace.get("selected_route", ""),
                    "selected_model": route_trace.get("selected_model", ""),
                    "tool_used": tool_trace.get("tool_name", ""),
                }

                st.session_state.latest_output = final_output
                st.session_state.latest_metadata = metadata
                st.session_state.latest_route_trace = route_trace
                st.session_state.latest_tool_trace = tool_trace
                st.session_state.latest_eval_saved = False

                st.success("Output generated with LLM routing and model-callable tool use.")

            except Exception as error:
                st.error("The output could not be generated.")
                st.exception(error)

    if st.session_state.latest_output:
        st.divider()
        st.header("Generated Output")

        with st.expander("LLM Routing Decision", expanded=True):
            st.json(st.session_state.latest_route_trace)

        with st.expander("Model Tool Use Trace", expanded=True):
            st.json(st.session_state.latest_tool_trace)

        st.markdown(st.session_state.latest_output)

        col_save, col_download = st.columns(2)

        with col_save:
            if st.button("Save Output", use_container_width=True):
                path = save_output(
                    st.session_state.latest_output,
                    st.session_state.latest_metadata,
                )
                st.success("Output saved.")
                st.write(f"Saved to: {path}")

        with col_download:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                "Download Output as Markdown",
                data=st.session_state.latest_output,
                file_name=f"project3_output_{timestamp}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        st.divider()
        st.header("Evaluation Record")

        expected_output = st.text_area(
            "Expected output",
            value=(
                "The app should select an LLM route, dispatch to a selected model, call analyze_project_request, "
                "and then generate a structured output using the tool result."
            ),
            height=130,
            key="expected_output",
        )

        actual_output = st.text_area(
            "Actual output",
            value=st.session_state.latest_output,
            height=220,
            key="actual_output",
        )

        if st.button("Save Evaluation Record", use_container_width=True):
            path = save_eval_record(
                expected_output=expected_output,
                actual_output=actual_output,
                metadata=st.session_state.latest_metadata,
                route_trace=st.session_state.latest_route_trace,
                tool_trace=st.session_state.latest_tool_trace,
            )
            st.session_state.latest_eval_saved = True
            st.success("Evaluation record saved.")
            st.write(f"Saved to: {path}")


def render_monitoring_tab():
    st.header("Monitoring / Change Detection")

    st.markdown(
        "Use this simple section to prove the app can compare an older input with an updated input."
    )

    previous_text = st.text_area("Previous text", height=180)
    updated_text = st.text_area("Updated text", height=180)

    if st.button("Compare Text"):
        if not previous_text.strip() or not updated_text.strip():
            st.error("Paste both previous and updated text.")
        else:
            result = compare_text_changes(previous_text, updated_text)
            save_monitoring_result(result)
            st.json(result)


def render_docs_tab():
    st.header("Project Documentation Helper")

    st.markdown(
        """
Use this section as a checklist while finishing Project 3.

### Required evidence to keep

- README explains what the app does.
- BUILD_LOG documents changes.
- Tests/eval_results.md includes expected vs actual results.
- Evidence folder includes screenshots or notes.
- App shows LLM routing and tool traces.
- Secrets are not committed.
"""
    )


def render_about_tab():
    st.header("About This Project 3 Shell")

    st.markdown(
        f"""
{APP_NAME} is a final project starter framework.

It was designed to carry forward the strongest parts of the earlier projects:

- Project 1: clear prompting, grounding, constraints, structured output, and evaluation.
- Project 2: Streamlit app structure, deployment readiness, demo/auth mode, saved outputs, monitoring, feedback/evaluation logs, and real model-callable tool use.
- Project 3 improvement: an LLM route decision is made before generation, and the app documents which route/model was selected.
"""
    )

    st.subheader("Workflow")

    st.graphviz_chart(
        """
        digraph {
            rankdir=LR;

            user_input [label="User enters request"];
            validation [label="Input validation"];
            router [label="LLM route selection"];
            model_dispatch [label="Select model by route"];
            tool_schema [label="Send tool schema"];
            model_tool_call [label="Model requests analyze_project_request"];
            app_tool [label="App executes local tool"];
            tool_result [label="Tool result returned"];
            output [label="Final structured output"];
            eval [label="Save eval record"];

            user_input -> validation;
            validation -> router;
            router -> model_dispatch;
            model_dispatch -> tool_schema;
            tool_schema -> model_tool_call;
            model_tool_call -> app_tool;
            app_tool -> tool_result;
            tool_result -> output;
            output -> eval;
        }
        """
    )

    st.subheader("Routing Explanation")

    st.write(
        "This app includes an LLM router that chooses a route. The code then maps that route to a model name. "
        "This is stronger than only changing prompt wording because the chosen route is recorded and used for dispatch."
    )

    st.subheader("Data Safety Notice")
    render_safety_notice()


def main():
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="🧭",
        layout="wide",
    )

    initialize_session_state()
    ensure_project_folders()
    render_auth_gate()
    render_header(APP_NAME, APP_SUBTITLE)
    render_welcome_panel()
    render_safety_notice()

    generate_tab, monitoring_tab, docs_tab, about_tab = st.tabs(
        ["Generate", "Monitoring", "Docs Checklist", "About"]
    )

    with generate_tab:
        render_generate_tab()

    with monitoring_tab:
        render_monitoring_tab()

    with docs_tab:
        render_docs_tab()

    with about_tab:
        render_about_tab()


if __name__ == "__main__":
    main()
