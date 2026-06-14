from collections import Counter
from datetime import datetime
import re


def clean_text(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def extract_keywords(text, limit=12):
    stop_words = {
        "about", "after", "again", "also", "and", "are", "because", "been",
        "before", "being", "could", "during", "each", "from", "have", "into",
        "more", "most", "not", "only", "other", "over", "said", "same",
        "that", "the", "their", "there", "these", "they", "this", "through",
        "under", "updated", "were", "what", "when", "where", "which",
        "while", "with", "would",
    }

    words = re.findall(r"\b[A-Za-z][A-Za-z0-9]{3,}\b", str(text).lower())
    filtered = [word for word in words if word not in stop_words]

    return [word for word, _count in Counter(filtered).most_common(limit)]


def estimate_complexity(text):
    word_count = len(clean_text(text).split())

    if word_count > 500:
        return "high"
    if word_count > 175:
        return "medium"
    return "low"


def analyze_project_request(user_request, output_style, project_goal):
    """
    Model-callable local tool.

    The LLM should request this tool before writing the final Project 3 output.
    The app executes this function and returns the structured result back to the model.
    """
    cleaned_request = clean_text(user_request)
    keywords = extract_keywords(cleaned_request, limit=15)
    complexity = estimate_complexity(cleaned_request)

    return {
        "tool_name": "analyze_project_request",
        "tool_executed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project_goal": project_goal,
        "output_style": output_style,
        "request_length": len(cleaned_request),
        "word_count": len(cleaned_request.split()),
        "complexity": complexity,
        "keywords": keywords,
        "likely_need": (
            "The user likely needs a structured, grounded output based on the provided request."
            if cleaned_request
            else "No usable request was provided."
        ),
        "information_gaps": [
            "Confirm the final target user.",
            "Confirm the exact decision or output the user needs.",
            "Confirm whether the input is public/synthetic and safe to use.",
            "Confirm how the output will be evaluated.",
        ],
        "recommended_output_elements": [
            "Bottom line or summary.",
            "Key findings.",
            "Reasoning based on provided input.",
            "Uncertainties or assumptions.",
            "Recommended next steps.",
        ],
        "analysis_limits": (
            "This tool only analyzes the user-provided input. It does not browse the web or independently verify facts."
        ),
    }
