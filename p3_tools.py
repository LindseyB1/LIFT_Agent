from collections import Counter
from datetime import datetime
import re


MAX_ANALYSIS_CHARS = 12000


RESOURCE_CATEGORY_TERMS = {
    "food": [
        "food", "pantry", "meal", "meals", "groceries", "grocery", "snap",
        "hungry", "formula", "diapers", "baby food"
    ],
    "housing": [
        "housing", "rent", "eviction", "shelter", "homeless", "apartment",
        "hotel", "motel", "utility", "utilities", "deposit", "mortgage",
        "landlord", "lease"
    ],
    "domestic_violence": [
        "domestic violence", "dv", "abuse", "unsafe", "threat", "threats",
        "ppo", "protective order", "advocate", "fled", "safety", "shelter"
    ],
    "legal": [
        "legal", "lawyer", "attorney", "court", "hearing", "divorce",
        "custody", "ppo", "small claims", "tenant", "landlord", "order"
    ],
    "medical_or_behavioral_health": [
        "medical", "doctor", "clinic", "hospital", "medication", "medicine",
        "therapy", "mental health", "urgent care", "insurance", "counseling"
    ],
    "transportation": [
        "transportation", "ride", "bus", "gas", "car", "vehicle", "uber",
        "lyft", "drive", "walking", "no car"
    ],
    "employment": [
        "job", "work", "employment", "resume", "interview", "career",
        "training", "unemployment"
    ],
    "veteran_support": [
        "veteran", "va", "dd214", "military", "guard", "reserve", "ssvf"
    ],
    "pet_or_service_animal_support": [
        "dog", "dogs", "cat", "cats", "pet", "pets", "service animal",
        "boarding", "foster", "vet", "veterinary"
    ],
    "language_access": [
        "spanish", "italian", "translator", "translation", "interpreter",
        "language", "bilingual", "english"
    ],
}


URGENCY_TERMS = {
    "high": [
        "tonight", "today", "right now", "now", "unsafe", "danger",
        "threatened", "kill", "hurt", "fled", "eviction notice", "evicted",
        "homeless", "no food", "hungry", "stranded", "emergency", "crisis",
        "sleep outside", "nowhere to go"
    ],
    "medium": [
        "tomorrow", "this week", "soon", "behind", "late", "deadline",
        "court", "hearing", "disconnect", "past due", "running out"
    ],
}


STOP_WORDS = {
    "about", "after", "again", "also", "and", "are", "because", "been",
    "before", "being", "could", "during", "each", "from", "have", "into",
    "more", "most", "not", "only", "other", "over", "said", "same",
    "that", "the", "their", "there", "these", "they", "this", "through",
    "under", "updated", "were", "what", "when", "where", "which", "while",
    "with", "would", "need", "help", "please", "near", "want", "looking",
    "trying", "find", "someone", "something"
}


def clean_text(text):
    """
    Normalize whitespace while preserving the user's original wording enough
    for keyword and urgency analysis.
    """
    return re.sub(r"\s+", " ", str(text or "")).strip()


def combine_request_context(user_request, uploaded_context=None):
    """
    Combine the typed user request with optional uploaded-file text.

    File upload parsing should happen in app.py. This helper only receives
    extracted text and adds it to the analysis context.
    """
    cleaned_request = clean_text(user_request)
    cleaned_upload = clean_text(uploaded_context)

    if cleaned_upload:
        combined = (
            f"User request:\n{cleaned_request}\n\n"
            f"Uploaded or attached context:\n{cleaned_upload}"
        )
    else:
        combined = cleaned_request

    return combined[:MAX_ANALYSIS_CHARS]


def extract_keywords(text, limit=15):
    """
    Extract keywords from longer LIFT-style user requests.

    This is intentionally simple and transparent. It is not meant to replace
    the LLM; it gives the tool result a readable explanation of what stood out.
    """
    words = re.findall(r"\b[A-Za-z][A-Za-z0-9'-]{2,}\b", str(text).lower())
    filtered = [word for word in words if word not in STOP_WORDS]

    return [word for word, _count in Counter(filtered).most_common(limit)]


def match_resource_categories(text):
    """
    Identify likely resource categories from the request.
    """
    normalized = clean_text(text).lower()
    matches = []

    for category, terms in RESOURCE_CATEGORY_TERMS.items():
        matched_terms = []
        for term in terms:
            if term in normalized:
                matched_terms.append(term)

        if matched_terms:
            matches.append(
                {
                    "category": category,
                    "score": len(matched_terms),
                    "matched_terms": matched_terms,
                }
            )

    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches


def detect_urgency_signal(text):
    """
    Detect urgency signals before keyword filtering so crisis phrases are not lost.
    This is a routing signal, not a legal, clinical, or safety determination.
    """
    normalized = clean_text(text).lower()

    high_matches = [term for term in URGENCY_TERMS["high"] if term in normalized]
    medium_matches = [term for term in URGENCY_TERMS["medium"] if term in normalized]

    if high_matches:
        return {
            "level": "high",
            "matched_terms": high_matches,
            "reason": (
                "The request includes language that may indicate same-day need, "
                "safety concern, homelessness, food insecurity, or crisis timing."
            ),
            "routing_note": (
                "Prioritize 24/7 resources, urgent backups, human review, and clear "
                "consent before outreach."
            ),
        }

    if medium_matches:
        return {
            "level": "medium",
            "matched_terms": medium_matches,
            "reason": "The request includes deadline or time-sensitive language.",
            "routing_note": (
                "Include follow-up timing, eligibility questions, and backup options."
            ),
        }

    return {
        "level": "low",
        "matched_terms": [],
        "reason": "No clear immediate crisis or deadline terms were detected.",
        "routing_note": "Proceed with standard resource matching and outreach planning.",
    }


def detect_information_gaps(text):
    """
    Identify missing details that would help LIFT match resources more accurately.
    """
    normalized = clean_text(text).lower()
    gaps = []

    if not any(term in normalized for term in ["grand rapids", "walker", "kentwood", "wyoming", "michigan", "mi", "zip", "address", "city", "county"]):
        gaps.append("location, city, county, or ZIP code")

    if not any(term in normalized for term in ["car", "bus", "walk", "walking", "ride", "transportation", "gas", "drive", "no car"]):
        gaps.append("transportation access")

    if not any(term in normalized for term in ["id", "license", "dd214", "lease", "court order", "ppo", "pay stub", "income", "benefits", "insurance"]):
        gaps.append("documents or eligibility proof available")

    if not any(term in normalized for term in ["child", "children", "dependent", "household", "family"]):
        gaps.append("household size or dependents")

    if not any(term in normalized for term in ["veteran", "va", "military", "guard", "reserve", "dd214"]):
        gaps.append("veteran or military-connected status, if relevant")

    if not any(term in normalized for term in ["dog", "dogs", "cat", "pet", "service animal"]):
        gaps.append("pet or service-animal needs, if relevant")

    if not any(term in normalized for term in ["spanish", "italian", "interpreter", "translator", "language"]):
        gaps.append("language access needs, if relevant")

    return gaps


def estimate_complexity(text, category_matches=None, urgency_signal=None, information_gaps=None):
    """
    Estimate complexity for LIFT routing.

    This version allows longer paragraph input. A paragraph is not automatically
    high complexity; complexity increases when the request has multiple need
    areas, urgency, and missing eligibility details.
    """
    cleaned = clean_text(text)
    word_count = len(cleaned.split())

    category_matches = category_matches or []
    urgency_signal = urgency_signal or {"level": "low"}
    information_gaps = information_gaps or []

    score = 0

    if word_count >= 50:
        score += 1
    if word_count >= 175:
        score += 1
    if word_count >= 400:
        score += 1

    if len(category_matches) >= 2:
        score += 1
    if len(category_matches) >= 4:
        score += 1

    if len(information_gaps) >= 4:
        score += 1

    if urgency_signal.get("level") == "medium":
        score += 1
    if urgency_signal.get("level") == "high":
        score += 2

    if score >= 5:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


def recommend_output_elements(category_matches, urgency_signal, information_gaps):
    """
    Recommend what the final LIFT output should include.
    """
    categories = {item["category"] for item in category_matches}

    elements = [
        "matched resource options",
        "eligibility questions",
        "warm outreach draft",
        "follow-up tracker rows",
        "human approval reminder before outreach",
    ]

    if urgency_signal.get("level") in {"medium", "high"}:
        elements.append("same-day or urgent backup options")

    if information_gaps:
        elements.append("missing-information checklist")

    if "transportation" in categories:
        elements.append("transportation workaround options")

    if "domestic_violence" in categories:
        elements.append("consent and safety reminder before any provider contact")

    if "legal" in categories:
        elements.append("legal document checklist")

    if "pet_or_service_animal_support" in categories:
        elements.append("pet or service-animal accommodation questions")

    if "language_access" in categories:
        elements.append("language-access or interpreter questions")

    return elements


def analyze_project_request(
    user_request,
    output_style="structured report",
    project_goal="LIFT resource matching and outreach",
    uploaded_context=None,
):
    """
    Model-callable local tool for LIFT Agent.

    The LLM may request this tool before the main resource-gap tool runs.
    The app executes this function and returns the structured result back to
    the model as a tool result.

    This tool does not browse the web, verify provider availability, contact
    providers, or make eligibility decisions. It only analyzes the user's
    typed request and optional uploaded-file context.
    """
    cleaned_request = clean_text(user_request)
    combined_context = combine_request_context(user_request, uploaded_context)

    keywords = extract_keywords(combined_context, limit=15)
    category_matches = match_resource_categories(combined_context)
    urgency_signal = detect_urgency_signal(combined_context)
    information_gaps = detect_information_gaps(combined_context)

    complexity = estimate_complexity(
        combined_context,
        category_matches=category_matches,
        urgency_signal=urgency_signal,
        information_gaps=information_gaps,
    )

    if category_matches:
        likely_need = category_matches[0]["category"]
    elif cleaned_request:
        likely_need = "general_resource_navigation"
    else:
        likely_need = "no_usable_request_provided"

    return {
        "tool_name": "analyze_project_request",
        "tool_mode": "OpenAI model-callable function tool",
        "tool_executed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project_goal": project_goal,
        "output_style": output_style,
        "request_length": len(cleaned_request),
        "combined_context_length": len(combined_context),
        "context_was_truncated_for_analysis": len(clean_text(user_request) + clean_text(uploaded_context)) > MAX_ANALYSIS_CHARS,
        "word_count": len(combined_context.split()),
        "complexity": complexity,
        "keywords": keywords,
        "likely_need": likely_need,
        "likely_resource_categories": category_matches,
        "urgency_signal": urgency_signal,
        "information_gaps": information_gaps,
        "recommended_output_elements": recommend_output_elements(
            category_matches,
            urgency_signal,
            information_gaps,
        ),
        "routing_guidance": {
            "should_continue_to_resource_gap_tool": True,
            "reason": (
                "This tool only interprets the user's need and context. "
                "The main LIFT resource-gap and contingency-planning tool should still run."
            ),
        },
        "analysis_limits": (
            "This tool analyzes user-provided text and optional uploaded-file text only. "
            "It does not browse the web, verify facts, check provider availability, "
            "or replace the external grounding and MCP-style provider check tools."
        ),
        "human_in_the_loop_note": (
            "This tool does not contact providers or make final eligibility decisions. "
            "The user should review and approve any outreach before it is sent."
        ),
    }