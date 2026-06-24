import json
import math
import os
import smtplib
import socket
import ssl
import time
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd
import streamlit as st

import ui_components as ui
from security_utils import validate_user_input

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
    OPENAI_IMPORT_ERROR = ""
except Exception as error:
    OpenAI = None
    OPENAI_AVAILABLE = False
    OPENAI_IMPORT_ERROR = str(error)


APP_NAME = "LIFT Agent"
APP_TAGLINE = "Locate. Identify. Follow-up. Track."
APP_SUBTITLE = "Provider matching, warm outreach drafting, basic provider checks, and follow-up tracking grounded in public external search results."

DEFAULT_MODEL = os.getenv("P3_DEFAULT_MODEL", "gpt-4o-mini")
PUBLIC_RESOURCE_SEARCH_API = "https://nominatim.openstreetmap.org/search"
HTTP_TIMEOUT_SECONDS = 8
CURATED_CORPUS_PATH = Path("Data/lift_curated_corpus.md")

# Supported languages
SUPPORTED_LANGUAGES = [
    "English",
    "Spanish",
    "Italian",
    "French",
    "Arabic",
    "Bengali / Bangla",
    "Swahili",
    "Kinyarwanda",
    "Nepali",
    "Vietnamese",
    "Burmese",
    "Karen",
    "Somali",
    "Haitian Creole",
    "Farsi",
    "Mandarin",
    "Hindi",
    "Telugu",
    "Other / Interpreter needed",
]

# Translation dictionary for core interface labels
TRANSLATIONS = {
    "English": {
        "Generate LIFT Plan": "Generate LIFT Plan",
        "Privacy, Consent, and User Control": "Privacy, Consent, and User Control",
        "Optional Context": "Optional Context",
        "Select only what you are comfortable sharing. This helps match better resources.": "Select only what you are comfortable sharing. This helps match better resources.",
        "Language / Idioma": "Language / Idioma",
        "Language access needed": "Language access needed",
        "No preference": "No preference",
        "Resource category": "Resource category",
        "Urgency": "Urgency",
        "Primary search location": "Primary search location",
        "Additional locations": "Additional locations",
        "Search radius in miles": "Search radius in miles",
        "Immediate / 24-7 Support Options": "Immediate / 24-7 Support Options",
        "Free or No-Cost Options": "Free or No-Cost Options",
        "After-Hours / Evening / Weekend Options": "After-Hours / Evening / Weekend Options",
        "Regular Business Hours Providers": "Regular Business Hours Providers",
        "Appointment-Only or Unknown Hours": "Appointment-Only or Unknown Hours",
        "Backup / Contingency Options": "Backup / Contingency Options",
        "Agent Decision Trace": "Agent Decision Trace",
        "Basic Provider Check": "Basic Provider Check",
        "Warm Outreach Draft": "Warm Outreach Draft",
        "Follow-up Tracker": "Follow-up Tracker",
        "Human approval required": "Human approval required",
        "No emails are sent automatically": "No emails are sent automatically",
        "Hours unknown": "Hours unknown",
        "Cost unknown": "Cost unknown",
        "Requirements unknown": "Requirements unknown",
        "Application required": "Application required",
        "Appointment needed": "Appointment needed",
        "Free": "Free",
        "Low-cost": "Low-cost",
        "Interpreter needed": "Interpreter needed",
        "Translation is AI-assisted. Please confirm important details directly with the provider.": "Translation is AI-assisted. Please confirm important details directly with the provider.",
    },
    "Spanish": {
        "Generate LIFT Plan": "Generar Plan LIFT",
        "Privacy, Consent, and User Control": "Privacidad, Consentimiento y Control del Usuario",
        "Optional Context": "Contexto Opcional",
        "Select only what you are comfortable sharing. This helps match better resources.": "Selecciona solo lo que te sientas cómodo compartiendo. Esto ayuda a encontrar mejores recursos.",
        "Language / Idioma": "Idioma",
        "Language access needed": "Idioma necesario",
        "No preference": "Sin preferencia",
        "Resource category": "Categoría de recurso",
        "Urgency": "Urgencia",
        "Primary search location": "Ubicación de búsqueda principal",
        "Additional locations": "Ubicaciones adicionales",
        "Search radius in miles": "Radio de búsqueda en millas",
        "Immediate / 24-7 Support Options": "Opciones de Apoyo Inmediato / 24-7",
        "Free or No-Cost Options": "Opciones Gratuitas o sin Costo",
        "After-Hours / Evening / Weekend Options": "Opciones Después de Horas / Noche / Fin de Semana",
        "Regular Business Hours Providers": "Proveedores de Horario Comercial Regular",
        "Appointment-Only or Unknown Hours": "Solo Cita Previa u Horas Desconocidas",
        "Backup / Contingency Options": "Opciones de Respaldo / Contingencia",
        "Agent Decision Trace": "Trazabilidad de Decisión del Agente",
        "Basic Provider Check": "Verificación Básica del Proveedor",
        "Warm Outreach Draft": "Borrador de Comunicación Cálida",
        "Follow-up Tracker": "Rastreador de Seguimiento",
        "Human approval required": "Se requiere aprobación humana",
        "No emails are sent automatically": "No se envían correos automáticamente",
        "Hours unknown": "Horario desconocido",
        "Cost unknown": "Costo desconocido",
        "Requirements unknown": "Requisitos desconocidos",
        "Application required": "Solicitud requerida",
        "Appointment needed": "Cita necesaria",
        "Free": "Gratis",
        "Low-cost": "Bajo costo",
        "Interpreter needed": "Se necesita intérprete",
        "Translation is AI-assisted. Please confirm important details directly with the provider.": "La traducción es asistida por IA. Por favor, confirma detalles importantes directamente con el proveedor.",
    },
    "Italian": {
        "Generate LIFT Plan": "Genera piano LIFT",
        "Privacy, Consent, and User Control": "Privacy, consenso e controllo utente",
        "Optional Context": "Contesto opzionale",
        "Select only what you are comfortable sharing. This helps match better resources.": "Seleziona solo cio che vuoi condividere. Aiuta LIFT a trovare risorse migliori.",
        "Language / Idioma": "Lingua",
        "Language access needed": "Supporto linguistico necessario",
        "No preference": "Nessuna preferenza",
        "Resource category": "Categoria risorsa",
        "Urgency": "Urgenza",
        "Primary search location": "Localita principale",
        "Additional locations": "Localita aggiuntive",
        "Search radius in miles": "Raggio di ricerca in miglia",
        "Hours unknown": "Orari sconosciuti",
        "Cost unknown": "Costo sconosciuto",
        "Free": "Gratuito",
        "Translation is AI-assisted. Please confirm important details directly with the provider.": "La traduzione e assistita dall'IA. Conferma i dettagli importanti direttamente con il fornitore.",
    },
    "French": {
        "Generate LIFT Plan": "Générer le Plan LIFT",
        "Privacy, Consent, and User Control": "Confidentialité, Consentement et Contrôle de l'Utilisateur",
        "Optional Context": "Contexte Facultatif",
        "Language / Idioma": "Langue",
        "Language access needed": "Accès linguistique nécessaire",
        "Resource category": "Catégorie de ressource",
        "Hours unknown": "Heures inconnues",
        "Cost unknown": "Coût inconnu",
        "Free": "Gratuit",
    },
    "Arabic": {
        "Generate LIFT Plan": "إنشاء خطة LIFT",
        "Privacy, Consent, and User Control": "الخصوصية والموافقة والتحكم من قبل المستخدم",
        "Optional Context": "سياق اختياري",
        "Language / Idioma": "اللغة",
        "Language access needed": "الحاجة إلى الوصول اللغوي",
        "Hours unknown": "ساعات غير معروفة",
        "Free": "مجاني",
    },
    "Bengali / Bangla": {
        "Generate LIFT Plan": "LIFT প্ল্যান তৈরি করুন",
        "Language / Idioma": "ভাষা",
        "Language access needed": "ভাষা অ্যাক্সেসের প্রয়োজন",
        "Hours unknown": "ঘন্টা অজানা",
        "Free": "বিনামূল্যে",
    },
    "Swahili": {
        "Generate LIFT Plan": "Tengeneza Mpango wa LIFT",
        "Language / Idioma": "Lugha",
        "Language access needed": "Mahitaji ya Kufikia Lugha",
        "Hours unknown": "Saa Haijulikani",
        "Free": "Bure",
    },
    "Hindi": {
        "Generate LIFT Plan": "LIFT योजना बनाएं",
        "Language / Idioma": "भाषा",
        "Language access needed": "भाषा पहुंच की आवश्यकता",
        "Hours unknown": "घंटे अज्ञात",
        "Free": "मुफ़्त",
    },
    "Telugu": {
        "Generate LIFT Plan": "LIFT ప్ల్యాన్‌ను సృష్టించండి",
        "Language / Idioma": "భాష",
        "Language access needed": "భాష ప్రాప్యత అవసరం",
        "Hours unknown": "సమయాలు తెలియవు",
        "Free": "ఉచితం",
    },
}


def get_text(key, language="English"):
    """Get translated text or fallback to English if not available."""
    if language not in TRANSLATIONS:
        language = "English"
    return TRANSLATIONS.get(language, TRANSLATIONS["English"]).get(key, key)


def current_language():
    """Return the selected display language from Streamlit session state."""
    return st.session_state.get("language", "English")


def t(key):
    """Short translation helper for Streamlit labels."""
    return get_text(key, current_language())


def translation_safety_note():
    """Show translation limitation when the user selects a non-English language."""
    if current_language() != "English":
        st.info(
            get_text(
                "Translation is AI-assisted. Please confirm important details directly with the provider.",
                current_language(),
            )
        )


ROUTES = [
    "resource_match",
    "location_radius_match",
    "gap_analysis",
    "validation_review",
    "outreach_email",
    "tracker_generation",
    "system_gap_brief",
    "fallback_review",
]


ANALYZE_RESOURCE_GAP_TOOL = {
    "type": "function",
    "function": {
        "name": "analyze_resource_gaps_and_build_contingency_plan",
        "description": (
            "Analyze a user's resource need, location/radius, eligibility context, and external public resource search data. "
            "Return matched resources, access gaps, eligibility barriers, contingency options, outreach draft, "
            "tracker rows, and system gap notes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_need": {"type": "string"},
                "resource_category": {"type": "string"},
                "primary_location": {"type": "string"},
                "additional_locations": {"type": "array", "items": {"type": "string"}},
                "radius_miles": {"type": "number"},
                "context": {"type": "object"},
                "selected_outputs": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "user_need",
                "resource_category",
                "primary_location",
                "additional_locations",
                "radius_miles",
                "context",
                "selected_outputs",
            ],
            "additionalProperties": False,
        },
    },
}

# MCP-style tool descriptor for model tool-calling
MCP_BASIC_PROVIDER_CHECK_TOOL = {
    "type": "function",
    "function": {
        "name": "mcp_basic_provider_check",
        "description": (
            "Basic provider information check (MCP-style). Returns website status, contact presence, hours, cost, "
            "appointment/application requirements, documents needed, confidence, notes, and limitations. Uses a basic public HTTP request when a website URL is available."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "provider_name": {"type": "string"},
                "website_url": {"type": "string"},
                "category": {"type": "string"},
                "location": {"type": "string"},
                "user_need": {"type": "string"},
            },
            "required": ["provider_name", "website_url"],
            "additionalProperties": False,
        },
    },
}


def get_openai_api_key():
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", "")
        if api_key:
            return api_key
    except Exception:
        pass

    return os.getenv("OPENAI_API_KEY", "")


def get_openai_client():
    api_key = get_openai_api_key()

    if not OPENAI_AVAILABLE:
        raise RuntimeError(f"OpenAI package is not available: {OPENAI_IMPORT_ERROR}")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing.")

    return OpenAI(api_key=api_key)


def parse_json_safely(text):
    if not text:
        return {}

    cleaned = str(text).strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except Exception:
        return {}


def infer_intent_fallback(user_need, resource_category, primary_location, context):
    """Create a transparent fallback interpretation for demo mode."""
    text = str(user_need or "").lower()
    missing_information = []

    if not str(primary_location or "").strip():
        missing_information.append("search location")
    if resource_category == "Any / Not Sure":
        missing_information.append("specific resource category")
    if context.get("transportation") == "Limited":
        missing_information.append("whether public transit or rides are possible")
    if context.get("documents_available") == "Not sure":
        missing_information.append("documents or eligibility proof available")

    need_type = resource_category
    if resource_category == "Any / Not Sure":
        if any(term in text for term in ["food", "pantry", "grocer", "meal"]):
            need_type = "Food / Basic Needs"
        elif any(term in text for term in ["rent", "housing", "shelter", "utility"]):
            need_type = "Housing / Utilities"
        elif any(term in text for term in ["ride", "bus", "transport"]):
            need_type = "Transportation"
        elif any(term in text for term in ["legal", "court", "lawyer"]):
            need_type = "Legal / Administrative"

    urgency = context.get("urgency", "Routine")
    if any(term in text for term in ["today", "tonight", "urgent", "emergency", "crisis", "right now"]):
        urgency = "Urgent"

    barriers = []
    if context.get("transportation") in {"No", "Limited", "Public transit only"}:
        barriers.append(f"Transportation: {context.get('transportation')}")
    if context.get("needs_24_7") in {"Yes", "Not sure"}:
        barriers.append(f"After-hours need: {context.get('needs_24_7')}")
    if context.get("documents_available") in {"No", "Not sure"}:
        barriers.append(f"Documents: {context.get('documents_available')}")
    barriers.extend(context.get("optional_context", []))

    return {
        "interpretation_mode": "DEMO FALLBACK - no live LLM interpretation",
        "need_type": need_type,
        "search_area": primary_location or "Grand Rapids, MI",
        "urgency": urgency,
        "barriers_or_preferences": barriers,
        "missing_information": missing_information,
        "plain_language_summary": (
            f"LIFT interpreted the request as a need for {need_type} near "
            f"{primary_location or 'Grand Rapids, MI'}."
        ),
    }


def llm_interpret_request(client, user_need, resource_category, primary_location, additional_locations, radius_miles, context):
    """Use the LLM to convert a short request into structured LIFT intent."""
    prompt = f"""
Interpret this LIFT Agent resource-navigation request.

Return JSON only with this schema:
{{
  "interpretation_mode": "LIVE LLM INTERPRETATION",
  "need_type": "short category or need",
  "search_area": "city/state or area to search",
  "urgency": "routine | soon | urgent | crisis_or_immediate",
  "barriers_or_preferences": ["barrier or preference"],
  "missing_information": ["specific missing detail"],
  "plain_language_summary": "one short user-friendly summary"
}}

Rules:
- Do not invent private facts.
- If the request is only a few words, infer cautiously and list missing information.
- Keep the answer practical for resource matching.

User request: {user_need}
Selected category: {resource_category}
Primary location: {primary_location}
Additional locations: {additional_locations}
Radius miles: {radius_miles}
Context: {json.dumps(context, indent=2)}
"""

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You interpret short resource-navigation requests into structured JSON for LIFT Agent.",
            },
            {"role": "user", "content": prompt.strip()},
        ],
        temperature=0,
    )
    parsed = parse_json_safely(response.choices[0].message.content or "")
    fallback = infer_intent_fallback(user_need, resource_category, primary_location, context)

    return {
        "interpretation_mode": "LIVE LLM INTERPRETATION",
        "need_type": parsed.get("need_type") or fallback["need_type"],
        "search_area": parsed.get("search_area") or fallback["search_area"],
        "urgency": parsed.get("urgency") or fallback["urgency"],
        "barriers_or_preferences": parsed.get("barriers_or_preferences") or fallback["barriers_or_preferences"],
        "missing_information": parsed.get("missing_information") or fallback["missing_information"],
        "plain_language_summary": parsed.get("plain_language_summary") or fallback["plain_language_summary"],
        "model": DEFAULT_MODEL,
    }


def provider_row_to_selection(row):
    """Normalize a matched-resource row for selected-provider session records."""
    return {
        "name": row.get("resource_name", "Unnamed resource"),
        "category": row.get("category", "Unknown"),
        "phone": row.get("phone", "N/A"),
        "email": row.get("group_email", "N/A"),
        "website": row.get("website", "N/A"),
        "business_hours": row.get("business_hours", "N/A"),
        "eligibility": row.get("eligibility", "N/A"),
        "city": row.get("city", "N/A"),
        "status": row.get("status", "Needs verification"),
        "distance_miles": row.get("distance_miles", ""),
    }


def build_followup_actions(selected_providers):
    """Create practical follow-up actions for the session case record."""
    actions = []
    for provider in selected_providers:
        actions.append(
            {
                "provider": provider.get("name", "Provider"),
                "next_action": "Verify eligibility, hours, intake process, and best contact method.",
                "status": "Not started",
                "contact_options": {
                    "phone": provider.get("phone", "N/A"),
                    "email": provider.get("email", "N/A"),
                    "website": provider.get("website", "N/A"),
                },
            }
        )
    return actions


def build_case_record(
    user_request,
    interpreted_intent,
    search_location,
    suggested_resources,
    selected_resources,
    provider_checks=None,
    case_id=None,
    created_at=None,
):
    """Build a session-only MVP case record."""
    timestamp = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "case_id": case_id or f"LIFT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "created_at": timestamp,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "storage_mode": "Session only unless the user downloads or exports this summary.",
        "user_request": user_request,
        "interpreted_intent": interpreted_intent,
        "search_location": search_location,
        "suggested_resource_count": len(suggested_resources or []),
        "suggested_resources": suggested_resources or [],
        "selected_resources": selected_resources or [],
        "provider_checks": provider_checks or [],
        "followup_actions": build_followup_actions(selected_resources or []),
    }


def format_case_summary(case_record):
    """Format a case record for user download."""
    lines = [
        "LIFT AGENT - SESSION CASE SUMMARY",
        f"Case ID: {case_record.get('case_id', '')}",
        f"Created: {case_record.get('created_at', '')}",
        f"Storage: {case_record.get('storage_mode', '')}",
        "",
        "USER REQUEST",
        str(case_record.get("user_request", "")),
        "",
        "INTERPRETED INTENT",
        json.dumps(case_record.get("interpreted_intent", {}), indent=2),
        "",
        "SELECTED RESOURCES",
    ]

    for provider in case_record.get("selected_resources", []):
        lines.append(f"- {provider.get('name')} | {provider.get('category')} | {provider.get('website')}")

    lines.extend(["", "FOLLOW-UP ACTIONS"])
    for action in case_record.get("followup_actions", []):
        lines.append(f"- {action.get('provider')}: {action.get('next_action')} [{action.get('status')}]")

    if case_record.get("provider_checks"):
        lines.extend(["", "PROVIDER CHECKS"])
        lines.append(json.dumps(case_record.get("provider_checks", []), indent=2))

    return "\n".join(lines)


def load_curated_corpus(path=CURATED_CORPUS_PATH):
    """
    Load the small curated LIFT corpus used for retrieval grounding.

    Chunking choice:
    - Each level-2 markdown section is a chunk.
    - This keeps citations human-readable and prevents unrelated guidance from
      being blended into one large context block.
    """
    corpus_path = Path(path)
    if not corpus_path.exists():
        return []

    chunks = []
    current_title = "Overview"
    current_lines = []

    for line in corpus_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if current_lines:
                chunks.append(
                    {
                        "citation_id": f"LIFT-CORPUS-{len(chunks) + 1}",
                        "source": corpus_path.as_posix(),
                        "title": current_title,
                        "content": "\n".join(current_lines).strip(),
                    }
                )
            current_title = line.replace("## ", "", 1).strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        chunks.append(
            {
                "citation_id": f"LIFT-CORPUS-{len(chunks) + 1}",
                "source": corpus_path.as_posix(),
                "title": current_title,
                "content": "\n".join(current_lines).strip(),
            }
        )

    return chunks


def retrieve_curated_context(user_need, resource_category, context, limit=3):
    """
    Retrieve the most relevant curated corpus chunks for the current request.

    This is intentionally deterministic so tests and evidence can explain why a
    citation was included.
    """
    chunks = load_curated_corpus()
    if not chunks:
        return {
            "retrieval_mode": "local_curated_corpus",
            "chunking": "markdown level-2 sections",
            "query_terms": [],
            "retrieved_chunks": [],
            "inline_citations": [],
        }

    query_text = " ".join(
        [
            str(user_need or ""),
            str(resource_category or ""),
            str(context.get("transportation", "")),
            str(context.get("needs_24_7", "")),
            str(context.get("documents_available", "")),
            " ".join(context.get("optional_context", [])),
        ]
    ).lower()
    query_terms = set(
        term
        for term in query_text.replace("/", " ").replace("-", " ").split()
        if len(term) >= 4
    )

    scored = []
    for chunk in chunks:
        chunk_text = chunk["content"].lower()
        score = sum(1 for term in query_terms if term in chunk_text)
        scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    selected = [
        chunk
        for score, chunk in scored[:limit]
        if score > 0
    ]

    if not selected:
        selected = [chunk for _score, chunk in scored[:1]]

    return {
        "retrieval_mode": "local_curated_corpus",
        "chunking": "markdown level-2 sections",
        "query_terms": sorted(query_terms),
        "retrieved_chunks": selected,
        "inline_citations": [chunk["citation_id"] for chunk in selected],
    }


def get_public_api_user_agent():
    contact = os.getenv("LIFT_CONTACT_EMAIL", "https://github.com/LindseyB1/LIFT_Agent")
    return f"LIFT-Agent-Project3/1.0 ({contact})"


def infer_city_state(address):
    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
        or address.get("county")
        or "Unknown"
    )
    state = address.get("state") or address.get("ISO3166-2-lvl4", "").split("-")[-1] or ""
    return city, state


def category_to_search_terms(resource_category, user_need):
    category_terms = {
        "Any / Not Sure": ["community resource", "social services", "211"],
        "Food / Basic Needs": ["food pantry", "food bank", "community food"],
        "Housing / Utilities": ["housing assistance", "homeless services", "utility assistance"],
        "Financial Assistance": ["financial assistance", "community action agency"],
        "Transportation": ["public transportation", "transportation assistance"],
        "Legal / Administrative": ["legal aid", "legal services"],
        "Behavioral Health": ["behavioral health", "mental health clinic"],
        "Emergency / 24-7 Crisis": ["crisis center", "emergency assistance", "988"],
        "Veteran / Service Member Support": ["veterans services", "veterans affairs"],
        "Family Readiness / FRG": ["family readiness", "military family support"],
        "General Support / 24-7 Navigation": ["211", "community resource navigation"],
    }

    terms = category_terms.get(resource_category, ["community resource"])
    if resource_category == "Any / Not Sure" and user_need:
        need_words = " ".join(str(user_need or "").split()[:8])
        return [need_words] + terms
    return terms


def normalize_nominatim_place(place, resource_category):
    address = place.get("address") or {}
    extra = place.get("extratags") or {}
    namedetails = place.get("namedetails") or {}
    city, state = infer_city_state(address)

    phone = extra.get("phone") or extra.get("contact:phone") or ""
    email = extra.get("email") or extra.get("contact:email") or ""
    website = extra.get("website") or extra.get("contact:website") or ""
    opening_hours = extra.get("opening_hours") or "Hours not returned by OSM"
    name = (
        namedetails.get("name")
        or place.get("name")
        or place.get("display_name", "").split(",")[0]
        or "Unnamed public search result"
    )

    return {
        "resource_name": name,
        "category": resource_category,
        "city": city,
        "state": state,
        "lat": float(place["lat"]),
        "lon": float(place["lon"]),
        "area_served": place.get("display_name", ""),
        "available_24_7": "Unknown",
        "business_hours": opening_hours,
        "phone": phone or "Not returned by API",
        "group_email": email or "Not returned by API",
        "website": website or "Not returned by API",
        "eligibility": "Not returned by public place-search API; confirm directly with provider.",
        "transportation_required": "Unknown",
        "remote_option": "Unknown",
        "last_verified_date": datetime.now().strftime("%Y-%m-%d"),
        "verification_method": "OpenStreetMap Nominatim public API search result",
        "status": "External API result - needs direct provider verification",
        "notes": (
            f"OSM class/type: {place.get('class', 'unknown')}/{place.get('type', 'unknown')}. "
            "Contact, eligibility, hours, and availability may be missing or outdated."
        ),
        "external_source": "OpenStreetMap Nominatim",
        "external_place_id": str(place.get("place_id", "")),
        "osm_type": place.get("osm_type", ""),
        "osm_id": str(place.get("osm_id", "")),
    }


def fetch_nominatim_search(query, limit=8):
    params = {
        "q": query,
        "format": "jsonv2",
        "addressdetails": 1,
        "extratags": 1,
        "namedetails": 1,
        "dedupe": 1,
        "limit": limit,
    }
    contact_email = os.getenv("LIFT_CONTACT_EMAIL", "")
    if "@" in contact_email:
        params["email"] = contact_email
    url = f"{PUBLIC_RESOURCE_SEARCH_API}?{urlencode(params)}"
    request = Request(
        url,
        headers={
            "User-Agent": get_public_api_user_agent(),
            "Accept": "application/json",
        },
    )

    with urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def fetch_external_resource_data(user_need, resource_category, primary_location, additional_locations, radius_miles):
    """
    Real public-data grounding layer.

    Calls OpenStreetMap Nominatim over HTTP and normalizes returned JSON into the
    columns used by the LIFT matching/gap tool.
    """

    locations = [primary_location] + list(additional_locations or [])
    location_text = "; ".join([loc for loc in locations if str(loc).strip()]) or "Grand Rapids, MI"
    queries = [f"{term} {location_text}" for term in category_to_search_terms(resource_category, user_need)][:3]

    trace = {
        "data_source": "OpenStreetMap Nominatim",
        "api_endpoint": PUBLIC_RESOURCE_SEARCH_API,
        "http_request_made": False,
        "queries": queries,
        "result_count": 0,
        "fallback_used": False,
        "errors": [],
        "usage_note": "Public OSM place-search data; provider details must still be confirmed directly.",
    }

    records = []
    seen_keys = set()

    for query in queries:
        try:
            trace["http_request_made"] = True
            if records or trace["errors"]:
                time.sleep(1)
            results = fetch_nominatim_search(query)
        except (HTTPError, URLError, TimeoutError, socket.timeout, json.JSONDecodeError) as error:
            trace["errors"].append(f"{query}: {type(error).__name__}: {error}")
            continue

        for place in results:
            key = (place.get("osm_type"), place.get("osm_id"), place.get("place_id"))
            if key in seen_keys or not place.get("lat") or not place.get("lon"):
                continue
            seen_keys.add(key)
            records.append(normalize_nominatim_place(place, resource_category))

    if records:
        trace["result_count"] = len(records)
        return pd.DataFrame(records), trace

    trace["fallback_used"] = True
    trace["usage_note"] = (
        "The external API returned no usable records or could not be reached. "
        "The app used labeled demo fallback rows so the workflow can still run."
    )
    fallback_df = synthetic_resource_data()
    trace["result_count"] = len(fallback_df)
    return fallback_df, trace


def synthetic_resource_data():
    """
    Synthetic/public-style resource data for the Project 3 draft.
    This is intentionally not a real operational directory.
    """

    rows = [
        {
            "resource_name": "Kent County Community Food Pantry",
            "category": "Food / Basic Needs",
            "city": "Grand Rapids",
            "state": "MI",
            "lat": 42.9634,
            "lon": -85.6681,
            "area_served": "Kent County",
            "available_24_7": "No",
            "business_hours": "Mon-Fri 9 AM-4 PM",
            "phone": "616-555-0101",
            "group_email": "intake@example.org",
            "website": "https://example.org/food",
            "eligibility": "Kent County residents; photo ID preferred",
            "transportation_required": "Yes",
            "remote_option": "No",
            "last_verified_date": "2026-06-01",
            "verification_method": "Synthetic record",
            "status": "Needs verification",
            "notes": "Business hours only; may be hard for third-shift users.",
        },
        {
            "resource_name": "Michigan 211 Navigation Line",
            "category": "General Support / 24-7 Navigation",
            "city": "Statewide",
            "state": "MI",
            "lat": 42.7335,
            "lon": -84.5555,
            "area_served": "Michigan",
            "available_24_7": "Yes",
            "business_hours": "24/7",
            "phone": "211",
            "group_email": "info@example211.org",
            "website": "https://mi211.org",
            "eligibility": "Open to public; resources may vary by ZIP code",
            "transportation_required": "No",
            "remote_option": "Yes",
            "last_verified_date": "2026-06-01",
            "verification_method": "Synthetic/public-style record",
            "status": "Usable starting point",
            "notes": "Good fallback when local resource fit is unclear.",
        },
        {
            "resource_name": "Veteran Emergency Assistance Office",
            "category": "Veteran / Service Member Support",
            "city": "Grand Rapids",
            "state": "MI",
            "lat": 42.9876,
            "lon": -85.7053,
            "area_served": "West Michigan",
            "available_24_7": "No",
            "business_hours": "Mon-Thu 8 AM-5 PM",
            "phone": "616-555-0202",
            "group_email": "veterans@example.org",
            "website": "https://example.org/veterans",
            "eligibility": "Veteran/service member status; proof of service may be requested",
            "transportation_required": "Sometimes",
            "remote_option": "Partial",
            "last_verified_date": "2026-05-20",
            "verification_method": "Synthetic record",
            "status": "Needs verification",
            "notes": "Potential DD214/proof-of-service barrier.",
        },
        {
            "resource_name": "After-Hours Crisis Support Line",
            "category": "Emergency / 24-7 Crisis",
            "city": "Statewide",
            "state": "MI",
            "lat": 42.3314,
            "lon": -83.0458,
            "area_served": "Michigan",
            "available_24_7": "Yes",
            "business_hours": "24/7",
            "phone": "988",
            "group_email": "crisis@example.org",
            "website": "https://example.org/crisis",
            "eligibility": "Open to public",
            "transportation_required": "No",
            "remote_option": "Yes",
            "last_verified_date": "2026-06-01",
            "verification_method": "Synthetic record",
            "status": "Usable starting point",
            "notes": "Emergency/crisis support; not a food/housing replacement.",
        },
        {
            "resource_name": "Housing Stabilization Intake",
            "category": "Housing / Utilities",
            "city": "Wyoming",
            "state": "MI",
            "lat": 42.9134,
            "lon": -85.7053,
            "area_served": "Kent County",
            "available_24_7": "No",
            "business_hours": "Mon-Fri 8:30 AM-4:30 PM",
            "phone": "616-555-0303",
            "group_email": "housing@example.org",
            "website": "https://example.org/housing",
            "eligibility": "Income and county eligibility may apply",
            "transportation_required": "Sometimes",
            "remote_option": "Partial",
            "last_verified_date": "2026-05-15",
            "verification_method": "Synthetic record",
            "status": "Needs verification",
            "notes": "Eligibility and documentation may be unclear.",
        },
        {
            "resource_name": "Community Transportation Voucher Program",
            "category": "Transportation",
            "city": "Walker",
            "state": "MI",
            "lat": 43.0014,
            "lon": -85.7681,
            "area_served": "Walker / Grand Rapids area",
            "available_24_7": "No",
            "business_hours": "Mon-Fri 9 AM-3 PM",
            "phone": "616-555-0404",
            "group_email": "transport@example.org",
            "website": "https://example.org/transport",
            "eligibility": "Appointment required; limited vouchers",
            "transportation_required": "No",
            "remote_option": "Yes",
            "last_verified_date": "2026-05-10",
            "verification_method": "Synthetic record",
            "status": "Needs verification",
            "notes": "Could support access to food, housing, medical, or legal resources.",
        },
        {
            "resource_name": "Legal Aid Intake Desk",
            "category": "Legal / Administrative",
            "city": "Grand Rapids",
            "state": "MI",
            "lat": 42.9709,
            "lon": -85.6700,
            "area_served": "West Michigan",
            "available_24_7": "No",
            "business_hours": "Mon-Fri 9 AM-5 PM",
            "phone": "616-555-0505",
            "group_email": "legal@example.org",
            "website": "https://example.org/legal",
            "eligibility": "Income and case-type screening may apply",
            "transportation_required": "Sometimes",
            "remote_option": "Partial",
            "last_verified_date": "2026-05-25",
            "verification_method": "Synthetic record",
            "status": "Needs verification",
            "notes": "Good example of eligibility screening barrier.",
        },
        {
            "resource_name": "Family Readiness Support Mailbox",
            "category": "Family Readiness / FRG",
            "city": "Lansing",
            "state": "MI",
            "lat": 42.7325,
            "lon": -84.5555,
            "area_served": "Michigan military-connected families",
            "available_24_7": "No",
            "business_hours": "Business hours",
            "phone": "517-555-0606",
            "group_email": "familyreadiness@example.mil",
            "website": "https://example.org/frg",
            "eligibility": "Service members, families, caregivers, dependents",
            "transportation_required": "No",
            "remote_option": "Yes",
            "last_verified_date": "2026-06-01",
            "verification_method": "Synthetic record",
            "status": "Stable contact preferred",
            "notes": "Uses stable group mailbox instead of relying on one changing POC.",
        },
    ]

    return pd.DataFrame(rows)


def check_provider_website_mcp_tool(provider_name, website_url, category, location):
    """
    MCP-style tool for basic provider website checking.

    Performs a basic public HTTP request when a usable website URL is available.
    It does not log in, bypass access controls, submit forms, or contact providers.

    Input:
      - provider_name: name of the provider
      - website_url: provider's website URL
      - category: resource category
      - location: provider location
      
    Output:
      - status: "reachable", "unreachable", or "unknown"
      - confidence: "high", "medium", or "low"
      - notes: verification notes
      - timestamp: when checked
      - limitations: tool limitations
    """
    
    tool_call_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    if not website_url or str(website_url).strip().lower().startswith("not returned"):
        return {
            "tool_name": "check_provider_website_mcp_tool",
            "provider_name": provider_name,
            "website_url": website_url,
            "category": category,
            "location": location,
            "status": "unknown",
            "http_status": None,
            "confidence": "low",
            "notes": "No provider website URL was returned by the external place-search API.",
            "website_components_found": [],
            "timestamp": tool_call_time,
            "limitations": [
                "The external place-search result did not include a URL to check.",
                "Confirm provider details directly before relying on them.",
            ],
            "recommendation": "Use phone, official directory records, or direct search to verify provider details.",
        }

    normalized_url = str(website_url).strip()
    if not normalized_url.startswith(("http://", "https://")):
        normalized_url = f"https://{normalized_url}"

    try:
        request = Request(
            normalized_url,
            headers={
                "User-Agent": get_public_api_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        with urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            status_code = response.getcode()
            content_type = response.headers.get("Content-Type", "")
            html = response.read(25000).decode("utf-8", errors="ignore").lower()

        components = []
        if any(term in html for term in ["phone", "tel:", "call us", "contact"]):
            components.append("phone_or_contact")
        if any(term in html for term in ["mailto:", "email"]):
            components.append("email")
        if any(term in html for term in ["hours", "open", "appointment"]):
            components.append("hours_or_appointment")
        if any(term in html for term in ["eligibility", "qualify", "requirements", "intake"]):
            components.append("eligibility_or_intake")

        confidence = "high" if status_code < 400 and components else "medium"
        notes = (
            f"HTTP {status_code}; content type {content_type or 'unknown'}. "
            f"Found public page signals: {', '.join(components) if components else 'none in first 25KB'}."
        )
        status = "reachable" if status_code < 400 else "unreachable"

    except (HTTPError, URLError, TimeoutError, socket.timeout, ValueError) as error:
        status_code = getattr(error, "code", None)
        components = []
        confidence = "medium" if status_code else "low"
        status = "unreachable"
        notes = f"Website check failed: {type(error).__name__}: {error}"

    return {
        "tool_name": "check_provider_website_mcp_tool",
        "provider_name": provider_name,
        "website_url": normalized_url,
        "category": category,
        "location": location,
        "status": status,
        "http_status": status_code,
        "confidence": confidence,
        "notes": notes,
        "website_components_found": components,
        "timestamp": tool_call_time,
        "limitations": [
            "This is a basic public HTTP check only; it does not execute JavaScript or submit forms.",
            "HTTP reachability is not proof that services are currently available.",
            "Tool assumes public websites only; does not access restricted or login-required pages.",
        ],
        "recommendation": "Always verify by phone or visit website directly before referring user."
    }


def mcp_basic_provider_check(provider_name, website_url, category=None, location=None, user_need=None):
    """
    Wrapper MCP tool that returns the specified schema required by the project.
    Internally uses `check_provider_website_mcp_tool` for a basic public HTTP check.

    Returns:
      - provider_name
      - website_status: active / unavailable / unknown / demo
      - confidence: high / medium / low
      - basic_contact_found: yes / no / unknown
      - hours_label
      - cost_label
      - application_required: yes / no / unknown
      - appointment_required: yes / no / unknown
      - documents_needed
      - notes
      - limitations
      - checked_at (timestamp)
    """
    raw = check_provider_website_mcp_tool(provider_name, website_url, category or "unknown", location or "unknown")

    # Map raw status to requested labels
    status_map = {
        "reachable": "active",
        "unreachable": "unavailable",
    }

    website_status = status_map.get(raw.get("status"), "unknown")
    confidence = raw.get("confidence", "low")

    # Heuristics for basic contact found
    components = raw.get("website_components_found", [])
    basic_contact_found = "yes" if any(c in components for c in ("phone_or_contact", "email")) else "no"

    hours_label = "Hours unknown"
    if "hours_or_appointment" in components:
        hours_label = "Hours or appointment language found on public page"

    # Cost/app/appointment/documents are unknown in demo mode
    cost_label = "Cost unknown"
    application_required = "unknown"
    appointment_required = "unknown"
    documents_needed = "unknown"

    checked_at = raw.get("timestamp")

    return {
        "provider_name": raw.get("provider_name"),
        "website_status": website_status,
        "http_status": raw.get("http_status"),
        "confidence": confidence,
        "basic_contact_found": basic_contact_found,
        "hours_label": hours_label,
        "cost_label": cost_label,
        "application_required": application_required,
        "appointment_required": appointment_required,
        "documents_needed": documents_needed,
        "notes": raw.get("notes"),
        "limitations": raw.get("limitations", []),
        "checked_at": checked_at,
    }


def get_secret_or_env(name, default=""):
    """Read a Streamlit secret first, then an environment variable."""
    try:
        value = st.secrets.get(name, "")
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv(name, default)


def log_agent_action(log_entries, action, status, data_source, message, detail=None, human_approval_required=False):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "status": status,
        "data_source": data_source,
        "message": message,
        "human_approval_required": "Yes" if human_approval_required else "No",
    }
    if detail is not None:
        entry["detail"] = detail
    log_entries.append(entry)
    return entry


def search_public_resources(user_need, resource_category, primary_location, additional_locations, radius_miles, log_entries):
    log_agent_action(
        log_entries,
        "Public resource search started",
        "completed",
        "real external API/tool data",
        "Searching public provider information with OpenStreetMap Nominatim.",
    )
    resources_df, data_source_trace = fetch_external_resource_data(
        user_need=user_need,
        resource_category=resource_category,
        primary_location=primary_location,
        additional_locations=additional_locations,
        radius_miles=radius_miles,
    )
    status = "fallback used" if data_source_trace.get("fallback_used") else "completed"
    source = "fallback/demo data" if data_source_trace.get("fallback_used") else "real external API/tool data"
    log_agent_action(
        log_entries,
        "Provider candidates found",
        status,
        source,
        f"{data_source_trace.get('result_count', len(resources_df))} provider candidate rows prepared.",
        data_source_trace,
    )
    return resources_df, data_source_trace


def check_provider_website(provider, log_entries):
    name = provider.get("resource_name") or provider.get("name") or "Provider"
    website_url = provider.get("website") or provider.get("Website") or ""
    check = mcp_basic_provider_check(
        provider_name=name,
        website_url=website_url,
        category=provider.get("category", ""),
        location=provider.get("city", provider.get("area_served", "")),
        user_need=st.session_state.get("user_need", ""),
    )
    status = "completed" if check.get("website_status") == "active" else "fallback used"
    data_source = "real external API/tool data" if check.get("http_status") else "local/session data"
    log_agent_action(
        log_entries,
        "Provider website checked",
        status,
        data_source,
        f"{name}: {check.get('website_status', 'unknown')}.",
        check,
    )
    return check


def google_maps_key_present():
    return bool(get_secret_or_env("GOOGLE_MAPS_API_KEY"))


def build_google_maps_link(address_or_lat_lng):
    """Build a Google Maps search link from an address string or lat/lng pair."""
    if isinstance(address_or_lat_lng, (tuple, list)) and len(address_or_lat_lng) >= 2:
        try:
            return f"https://www.google.com/maps/search/?api=1&query={float(address_or_lat_lng[0])},{float(address_or_lat_lng[1])}"
        except (TypeError, ValueError):
            return ""
    query = str(address_or_lat_lng or "").strip()
    if not query:
        return ""
    return f"https://www.google.com/maps/search/?api=1&query={urlencode({'q': query})[2:]}"


def geocode_location_google(location_text, api_key):
    """Geocode one user-entered location with Google Maps. Returns a status dict."""
    if not str(location_text or "").strip():
        return {"location_text": location_text, "status": "skipped", "error": "No location text provided."}
    if not api_key:
        return {"location_text": location_text, "status": "skipped", "error": "GOOGLE_MAPS_API_KEY is not configured."}

    try:
        params = urlencode({"address": location_text, "key": api_key})
        url = f"https://maps.googleapis.com/maps/api/geocode/json?{params}"
        request = Request(url, headers={"User-Agent": get_public_api_user_agent()})
        with urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if payload.get("status") == "OK" and payload.get("results"):
            result = payload["results"][0]
            coords = result["geometry"]["location"]
            lat = float(coords["lat"])
            lon = float(coords["lng"])
            return {
                "location_text": location_text,
                "status": "completed",
                "formatted_address": result.get("formatted_address", location_text),
                "lat": lat,
                "lon": lon,
                "map_link": build_google_maps_link((lat, lon)),
            }
        return {
            "location_text": location_text,
            "status": "failed",
            "error": payload.get("status", "unknown"),
        }
    except Exception as error:
        return {
            "location_text": location_text,
            "status": "failed",
            "error": f"{type(error).__name__}: {error}",
        }


def geocode_search_locations(primary_location, additional_locations, log_entries):
    api_key = get_secret_or_env("GOOGLE_MAPS_API_KEY")
    locations = [primary_location] + list(additional_locations or [])
    locations = [loc for loc in locations if str(loc or "").strip()]

    if not api_key:
        log_agent_action(
            log_entries,
            "Google Maps/geocoding",
            "skipped",
            "local/session data",
            "GOOGLE_MAPS_API_KEY is not configured. LIFT will use typed location text and any coordinates from public search results.",
        )
        return {"configured": False, "locations": [], "completed_count": 0, "failed_count": 0}

    results = [geocode_location_google(location, api_key) for location in locations]
    completed = [result for result in results if result.get("status") == "completed"]
    failed = [result for result in results if result.get("status") == "failed"]
    status = "completed" if completed else "failed"
    message = (
        f"{len(completed)} search location(s) geocoded with Google Maps."
        if completed
        else "Google Maps geocoding was configured but no search locations were geocoded."
    )
    log_agent_action(
        log_entries,
        "Google Maps/geocoding",
        status,
        "real external API/tool data",
        message,
        {"completed_count": len(completed), "failed_count": len(failed), "locations": results},
    )
    return {
        "configured": True,
        "locations": results,
        "completed_count": len(completed),
        "failed_count": len(failed),
    }


def geocode_provider_locations(provider_rows, api_key=None, log_entries=None):
    if isinstance(api_key, list) and log_entries is None:
        log_entries = api_key
        api_key = None
    if api_key is None:
        api_key = get_secret_or_env("GOOGLE_MAPS_API_KEY")
    log_entries = log_entries if log_entries is not None else []
    providers = provider_rows or []
    if not api_key:
        log_agent_action(
            log_entries,
            "Provider map links created",
            "skipped",
            "local/session data",
            "GOOGLE_MAPS_API_KEY is not configured. Existing coordinates and typed locations are used for map links when possible.",
        )
        updated = []
        for provider in providers:
            row = dict(provider)
            row.setdefault("geocoding_status", "skipped")
            if row.get("lat") not in ["", None] and row.get("lon") not in ["", None]:
                row["map_link"] = row.get("map_link") or build_google_maps_link((row.get("lat"), row.get("lon")))
            else:
                row["map_link"] = row.get("map_link") or build_google_maps_link(row.get("area_served") or row.get("city"))
            updated.append(row)
        return updated, {"configured": False, "geocoded_count": 0, "errors": []}

    geocoded = []
    errors = []
    for provider in providers:
        updated = dict(provider)
        updated.setdefault("geocoding_status", "not attempted")
        if updated.get("lat") not in ["", None] and updated.get("lon") not in ["", None]:
            updated["map_link"] = updated.get("map_link") or build_google_maps_link((updated.get("lat"), updated.get("lon")))
            updated["geocoding_status"] = "existing coordinates"
            geocoded.append(updated)
            continue
        query = (
            updated.get("area_served")
            or " ".join(
                str(updated.get(part, ""))
                for part in ["resource_name", "city", "state"]
                if updated.get(part)
            )
        )
        if not query.strip():
            errors.append(f"{updated.get('resource_name', 'Provider')}: no mappable address.")
            updated["geocoding_status"] = "skipped"
            geocoded.append(updated)
            continue
        try:
            result = geocode_location_google(query, api_key)
            if result.get("status") == "completed":
                updated["lat"] = result["lat"]
                updated["lon"] = result["lon"]
                updated["map_link"] = result["map_link"]
                updated["geocode_source"] = "Google Maps Geocoding API"
                updated["geocoding_status"] = "completed"
            else:
                updated["geocoding_status"] = "failed"
                updated["map_link"] = updated.get("map_link") or build_google_maps_link(query)
                errors.append(f"{updated.get('resource_name', 'Provider')}: {result.get('error', 'unknown')}")
        except Exception as error:
            updated["geocoding_status"] = "failed"
            updated["map_link"] = updated.get("map_link") or build_google_maps_link(query)
            errors.append(f"{updated.get('resource_name', 'Provider')}: {type(error).__name__}: {error}")
        geocoded.append(updated)
        time.sleep(0.1)

    count = sum(1 for provider in geocoded if provider.get("geocode_source") == "Google Maps Geocoding API")
    linked_count = sum(1 for provider in geocoded if provider.get("map_link"))
    status = "completed" if linked_count else "failed"
    log_agent_action(
        log_entries,
        "Provider map links created",
        status,
        "real external API/tool data",
        f"{count} provider location(s) geocoded and {linked_count} provider map link(s) prepared with Google Maps.",
        {"configured": True, "geocoded_count": count, "map_link_count": linked_count, "errors": errors},
    )
    return geocoded, {"configured": True, "geocoded_count": count, "map_link_count": linked_count, "errors": errors}


def render_google_map_or_pydeck_map(providers=None, log_entries=None):
    return render_google_map(providers or st.session_state.get("tool_result", {}).get("matched_resources", []), log_entries or [])


def render_google_map(providers, log_entries):
    mapped = []
    for provider in providers:
        try:
            lat = float(provider.get("lat"))
            lon = float(provider.get("lon"))
            mapped.append(
                {
                    "resource_name": provider.get("resource_name", "Provider"),
                    "lat": lat,
                    "lon": lon,
                    "map_link": provider.get("map_link") or f"https://www.google.com/maps/search/?api=1&query={lat},{lon}",
                }
            )
        except (TypeError, ValueError):
            continue
    if mapped:
        log_agent_action(
            log_entries,
            "Map rendered with provider markers/map links",
            "completed" if google_maps_key_present() else "fallback used",
            "real external API/tool data" if google_maps_key_present() else "local/session data",
            f"{len(mapped)} provider(s) available for map display.",
            human_approval_required=False,
        )
    else:
        log_agent_action(
            log_entries,
            "Map rendered with provider markers/map links",
            "skipped",
            "local/session data",
            "No complete provider coordinates were available to map.",
        )
    return mapped


def generate_outreach_email(user_need, provider, language_access_needed="No preference"):
    provider_name = provider.get("resource_name") or provider.get("name") or "the provider"
    category = provider.get("category", "resource support")
    return {
        "recipient": provider.get("group_email", "") if "@" in str(provider.get("group_email", "")) else "",
        "subject": f"Resource Fit / Eligibility Confirmation - {category}",
        "body": (
            "Hello,\n\n"
            f"I am reaching out to confirm whether {provider_name} may be a fit for someone seeking support related to: {user_need}\n\n"
            "Could you please confirm:\n"
            "1. Whether your program currently provides this type of support\n"
            "2. Eligibility requirements, including location, age, income, military/veteran/family status, or documentation\n"
            "3. Current hours and whether after-hours or remote options exist\n"
            "4. Best intake method: phone, email, website, walk-in, appointment, or referral\n"
            "5. Whether transportation or in-person attendance is required\n"
            f"6. Whether {language_access_needed} language support or interpreter support is available\n\n"
            "I am not asking for a referral through this message yet. I am only trying to verify fit, availability, and next steps.\n\n"
            "Thank you."
        ),
    }


def generate_call_script(user_need, provider, language_access_needed="No preference"):
    provider_name = provider.get("resource_name") or provider.get("name") or "the provider"
    return (
        "LIFT does not place phone calls. This script is prepared for the user to review and use when calling.\n\n"
        f"Hi, is this {provider_name}? I am calling to verify a few things for someone looking for help with: {user_need}\n\n"
        "1. Do you currently provide this type of support?\n"
        "2. What are the key eligibility requirements?\n"
        "3. What are your hours, and do you have after-hours or 24/7 options?\n"
        "4. Is an appointment, referral, walk-in visit, or application required?\n"
        "5. What documents should the person bring or prepare?\n"
        "6. Is there a cost, waitlist, transportation issue, or service-area limit?\n"
        f"7. Do you have {language_access_needed} language support or interpreter access?\n\n"
        "Thank you. I am gathering accurate next-step information before someone relies on this resource."
    )


def export_tracker_csv(tracker_rows, log_entries=None):
    tracker_df = pd.DataFrame(tracker_rows or [])
    csv_data = tracker_df.to_csv(index=False)
    if log_entries is not None:
        log_agent_action(
            log_entries,
            "CSV tracker export created",
            "completed" if tracker_rows else "skipped",
            "local/session data",
            f"{len(tracker_rows or [])} tracker row(s) exported to CSV data.",
        )
    return csv_data


def classify_provider_category(provider):
    text = f"{provider.get('category', '')} {provider.get('resource_name', '')} {provider.get('notes', '')}".lower()
    if any(term in text for term in ["food", "pantry", "meal"]):
        return "Food"
    if any(term in text for term in ["shelter", "housing", "homeless"]):
        return "Shelter"
    if "legal" in text:
        return "Legal"
    if any(term in text for term in ["medical", "health", "clinic", "behavioral"]):
        return "Medical"
    if "transport" in text or "bus" in text:
        return "Transportation"
    if any(term in text for term in ["utility", "utilities", "bill"]):
        return "Utility Help"
    return "Other"


def provider_confidence_label(provider, check=None, fallback_used=False):
    has_address = bool(provider.get("area_served") or provider.get("city"))
    has_coords = provider.get("lat") not in ["", None] and provider.get("lon") not in ["", None]
    website_reachable = bool(check and check.get("website_status") == "active")
    category_match = provider.get("category") not in ["", None, "Any / Not Sure"]
    if fallback_used or "fallback" in str(provider.get("matched_location", "")).lower():
        return "Low confidence", "Limited public information or fallback/example data used; needs human confirmation."
    if website_reachable and (has_address or has_coords) and category_match:
        return "High confidence", "Website reachable, location available, and category appears to match the need."
    if category_match or has_address or has_coords:
        return "Medium confidence", "Provider appears relevant, but hours, eligibility, or availability need confirmation."
    return "Low confidence", "Limited public information, missing address, or unreachable website."


def next_best_provider_action(provider, confidence_label):
    text = f"{provider.get('eligibility', '')} {provider.get('business_hours', '')} {provider.get('notes', '')}".lower()
    if "document" in text or "proof" in text or "id" in text:
        return "Confirm documents before traveling."
    if "hours" in text or "unknown" in text or confidence_label != "High confidence":
        return "Call to confirm walk-in hours and current availability."
    if "email" in str(provider.get("group_email", "")).lower() or "@" in str(provider.get("group_email", "")):
        return "Email to ask about eligibility and intake steps."
    return "Use as backup if the first option is full or does not fit."


def build_map_summary(providers, provider_checks, map_rows, radius_miles):
    provider_checks = provider_checks or []
    reachable_names = {
        check.get("provider_name")
        for check in provider_checks
        if check.get("website_status") == "active"
    }
    distances = [
        (provider.get("resource_name", "Provider"), provider.get("distance_miles"))
        for provider in providers
        if provider.get("distance_miles") not in ["", None]
    ]
    distances = sorted(distances, key=lambda item: item[1] if item[1] is not None else 9999)
    categories = sorted({classify_provider_category(provider) for provider in providers})
    confirmation_count = max(len(providers) - len(reachable_names), 0)
    closest = distances[0][0] if distances else "Distance not available"
    gaps = []
    if "Legal" not in categories:
        gaps.append("Legal aid may require a broader search radius.")
    if not map_rows:
        gaps.append("Some locations could not be mapped from available public data.")
    if radius_miles <= 10 and len(providers) < 3:
        gaps.append("Few nearby options found; consider a wider radius.")
    if not gaps:
        gaps.append("Coverage appears usable, but availability still needs human confirmation.")
    suggested = "Start with the closest high or medium confidence provider, then use the tracker to confirm hours and eligibility."
    return {
        "total_providers": len(providers),
        "closest_provider": closest,
        "reachable_websites": len(reachable_names),
        "needs_human_confirmation": confirmation_count,
        "categories": categories,
        "coverage_concerns": gaps,
        "suggested_next_action": suggested,
        "summary_text": (
            f"Map Summary: LIFT found {len(providers)} possible resource option(s) within the selected area. "
            f"{len(reachable_names)} have reachable websites. {confirmation_count} need human confirmation. "
            f"Categories represented: {', '.join(categories) if categories else 'none returned'}. {suggested}"
        ),
    }


def send_email_smtp(to_address, subject, body):
    required = {
        "SMTP_HOST": get_secret_or_env("SMTP_HOST"),
        "SMTP_PORT": get_secret_or_env("SMTP_PORT", "587"),
        "SMTP_USER": get_secret_or_env("SMTP_USER"),
        "SMTP_PASSWORD": get_secret_or_env("SMTP_PASSWORD"),
        "SMTP_FROM": get_secret_or_env("SMTP_FROM"),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        return {"sent": False, "status": "skipped", "message": f"Missing SMTP configuration: {', '.join(missing)}"}
    if not to_address or "@" not in to_address:
        return {"sent": False, "status": "skipped", "message": "Recipient email address is missing or invalid."}

    message = EmailMessage()
    message["From"] = required["SMTP_FROM"]
    message["To"] = to_address
    message["Subject"] = subject
    message.set_content(body)

    try:
        port = int(required["SMTP_PORT"])
        context = ssl.create_default_context()
        with smtplib.SMTP(required["SMTP_HOST"], port, timeout=HTTP_TIMEOUT_SECONDS) as server:
            server.starttls(context=context)
            server.login(required["SMTP_USER"], required["SMTP_PASSWORD"])
            server.send_message(message)
        return {"sent": True, "status": "completed", "message": "Approved email sent by SMTP."}
    except Exception as error:
        return {"sent": False, "status": "failed", "message": f"{type(error).__name__}: {error}"}


def create_tracker_rows(tool_result, log_entries):
    rows = tool_result.get("tracker_rows", [])
    log_agent_action(
        log_entries,
        "Tracker rows created",
        "completed" if rows else "skipped",
        "local/session data",
        f"{len(rows)} tracker row(s) prepared.",
    )
    return rows


def add_optional_context_to_tracker_rows(tool_result, context):
    rows = tool_result.get("tracker_rows", [])
    for row in rows:
        row["user_preferred_contact_method"] = context.get("user_preferred_contact_method", "")
        row["user_outreach_language"] = context.get("user_outreach_language", "")
        row["user_email_provided"] = context.get("user_email_provided", "no")
        row["supporting_files_count"] = context.get("supporting_files_count", 0)
        row["supporting_links_count"] = len(context.get("supporting_links", []))
        row["notes_from_user_context"] = context.get("notes_from_user_context", "")
    return rows


def write_agent_audit_log(log_entries):
    st.session_state["agent_activity_log"] = log_entries
    return log_entries


LOCATION_COORDS = {
    "grand rapids, mi": (42.9634, -85.6681),
    "walker, mi": (43.0014, -85.7681),
    "kentwood, mi": (42.8695, -85.6447),
    "wyoming, mi": (42.9134, -85.7053),
    "east lansing, mi": (42.7369, -84.4839),
    "lansing, mi": (42.7325, -84.5555),
    "statewide, mi": (42.7335, -84.5555),
}


def normalize_location(location):
    return str(location or "").strip().lower()


def get_location_coords(location):
    normalized = normalize_location(location)
    return LOCATION_COORDS.get(normalized)


def haversine_miles(lat1, lon1, lat2, lon2):
    radius_earth_miles = 3958.8
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_earth_miles * c


def filter_resources_by_category_and_location(resources, category, locations, radius_miles):
    working = resources.copy()

    if category != "Any / Not Sure":
        exact = working[working["category"] == category]
        if not exact.empty:
            working = exact
        else:
            working = working[
                working["category"].str.contains(category.split("/")[0].strip(), case=False, na=False)
            ]

    location_points = []
    for location in locations:
        coords = get_location_coords(location)
        if coords:
            location_points.append((location, coords[0], coords[1]))

    if not location_points:
        working["distance_miles"] = None
        working["matched_location"] = "No known coordinate match"
        return working

    distance_records = []

    for _, row in working.iterrows():
        nearest_distance = None
        nearest_location = None

        for location_name, lat, lon in location_points:
            distance = haversine_miles(lat, lon, row["lat"], row["lon"])

            if nearest_distance is None or distance < nearest_distance:
                nearest_distance = distance
                nearest_location = location_name

        row_dict = row.to_dict()
        row_dict["distance_miles"] = round(nearest_distance, 1) if nearest_distance is not None else None
        row_dict["matched_location"] = nearest_location
        distance_records.append(row_dict)

    filtered = pd.DataFrame(distance_records)

    statewide_mask = filtered["city"].str.lower().eq("statewide")
    radius_mask = filtered["distance_miles"].fillna(9999) <= radius_miles

    return filtered[statewide_mask | radius_mask].sort_values(
        by=["available_24_7", "distance_miles"], ascending=[False, True]
    )


def analyze_resource_gaps_and_build_contingency_plan(
    user_need,
    resource_category,
    primary_location,
    additional_locations,
    radius_miles,
    context,
    selected_outputs,
    resource_data,
):
    """
    Custom Project 3 tool.

    It analyzes resource fit, access barriers, eligibility issues, validation flags,
    contingency plans, outreach drafts, tracker rows, and system gap notes.
    """

    locations = [primary_location] + list(additional_locations or [])
    locations = [loc.strip() for loc in locations if str(loc).strip()]

    resources = pd.DataFrame(resource_data)
    matches = filter_resources_by_category_and_location(
        resources=resources,
        category=resource_category,
        locations=locations,
        radius_miles=radius_miles,
    )

    if matches.empty:
        matches = resources.head(3).copy()
        matches["distance_miles"] = None
        matches["matched_location"] = "Fallback match"

    matches = matches.head(5)

    fit_concerns = []
    eligibility_barriers = []
    access_barriers = []
    twenty_four_seven_gaps = []
    validation_flags = []

    needs_24_7 = context.get("needs_24_7") == "Yes"
    transportation = context.get("transportation")
    documentation = context.get("documents_available")
    audience = context.get("audience")

    for _, row in matches.iterrows():
        name = row["resource_name"]

        if str(row["status"]).lower().startswith("needs"):
            validation_flags.append(f"{name}: contact details should be verified before relying on this resource.")

        if needs_24_7 and row["available_24_7"] != "Yes":
            twenty_four_seven_gaps.append(f"{name}: not 24/7; may fail for urgent or third-shift access.")

        if transportation in ["No", "Limited", "Public transit only"] and row["transportation_required"] in [
            "Yes",
            "Sometimes",
        ]:
            access_barriers.append(
                f"{name}: transportation may be a barrier because the user selected '{transportation}'."
            )

        if documentation in ["No", "Not sure"] and any(
            term in str(row["eligibility"]).lower()
            for term in ["proof", "photo id", "income", "dd214", "service"]
        ):
            eligibility_barriers.append(f"{name}: eligibility may require documentation or screening.")

        if audience == "Community member" and "service" in str(row["eligibility"]).lower():
            eligibility_barriers.append(f"{name}: may be limited to military-connected users.")

    if not fit_concerns:
        fit_concerns.append(
            "Resource fit depends on eligibility, current availability, hours, transportation, and verification status."
        )

    if not validation_flags:
        validation_flags.append(
            "No major validation issue identified in the returned data, but real-world use requires phone/website verification."
        )

    contingency_plans = [
        {
            "plan": "Plan A",
            "title": "Use the closest matching resource first",
            "steps": [
                "Contact the best-fit provider using the stable office phone, group email, or official website.",
                "Confirm eligibility, hours, documents required, and whether appointments are needed.",
                "Record the result in the tracker and set a follow-up date.",
            ],
        },
        {
            "plan": "Plan B",
            "title": "Use a 24/7 or remote navigation fallback",
            "steps": [
                "If the best-fit provider is closed, unreachable, or business-hours only, use a 24/7 navigation line or remote option.",
                "Ask for resources that match the user’s location, transportation limits, eligibility, and urgency.",
                "Record any new referrals and flag repeated barriers.",
            ],
        },
        {
            "plan": "Plan C",
            "title": "Escalate the access gap",
            "steps": [
                "If multiple resources fail for the same reason, summarize the barrier as a system gap.",
                "Identify whether the issue is hours, transportation, eligibility, documentation, location, or outdated contact data.",
                "Prepare a short gap brief for SRWC/FRG/resource coordinators or support staff.",
            ],
        },
    ]

    best_match = matches.iloc[0].to_dict()

    outreach_email = f"""Subject: Resource Fit / Eligibility Confirmation Request

Hello,

I am trying to confirm whether your program may be a fit for someone seeking support related to: {user_need}

Could you please confirm:
1. Whether your program currently provides this type of support
2. Eligibility requirements, including location, age, income, military/veteran/family status, or documentation
3. Current hours and whether any after-hours or remote options exist
4. Best intake method: phone, email, website, walk-in, appointment, or referral
5. Whether transportation or in-person pickup is required

I am not asking you to accept a referral through this message yet. I am only trying to verify fit, availability, and next steps before sending someone in the wrong direction.

Thank you."""

    tracker_rows = []

    for _, row in matches.iterrows():
        tracker_rows.append(
            {
                "Case ID": f"LIFT-{datetime.now().strftime('%Y%m%d')}-001",
                "Need Category": resource_category,
                "User Need": user_need,
                "Resource Name": row["resource_name"],
                "Matched Location": row.get("matched_location", ""),
                "Distance Miles": row.get("distance_miles", ""),
                "Contact Method": "Phone / Email / Website",
                "Phone": row["phone"],
                "Email": row["group_email"],
                "Website": row["website"],
                "Status": "Pending Outreach",
                "Progress %": 10,
                "Follow-Up Due Date": "",
                "Barrier Identified": "; ".join(
                    [
                        flag
                        for flag in access_barriers + eligibility_barriers + twenty_four_seven_gaps
                        if row["resource_name"] in flag
                    ]
                ),
                "Next Action": "Verify eligibility, hours, availability, and intake process.",
                "Outcome": "",
                "Notes": row["notes"],
            }
        )

    system_gap_notes = [
        "This draft uses public external place-search data when available; provider details still require direct verification.",
        "Repeated barriers should be tracked by type: transportation, documentation, eligibility, location, hours, or outdated contact information.",
        "Future production versions could add consent-based email/voicemail review, login, audit logs, and limited permissions.",
    ]
    retrieval_trace = context.get("retrieval_trace", {})
    citations = retrieval_trace.get("inline_citations", [])

    if citations:
        system_gap_notes.append(
            "Curated guidance used for this plan: " + ", ".join(citations) + "."
        )

    if twenty_four_seven_gaps:
        system_gap_notes.append("Potential system gap: selected need may not have enough 24/7 or after-hours coverage.")

    if access_barriers:
        system_gap_notes.append("Potential system gap: transportation limits may prevent access to listed resources.")

    return {
        "matched_resources": matches.to_dict(orient="records"),
        "fit_concerns": fit_concerns,
        "eligibility_barriers": eligibility_barriers,
        "access_barriers": access_barriers,
        "twenty_four_seven_gaps": twenty_four_seven_gaps,
        "validation_flags": validation_flags,
        "contingency_plans": contingency_plans,
        "outreach_email_draft": outreach_email,
        "tracker_rows": tracker_rows,
        "system_gap_notes": system_gap_notes,
        "recommended_first_resource": best_match.get("resource_name", ""),
        "retrieval_trace": retrieval_trace,
        "citations": citations,
    }


def demo_route_decision(user_need, resource_category, context):
    """
    Demo fallback when no API key is available.
    Clearly labeled so it is not represented as a live LLM decision.
    """

    text = f"{user_need} {resource_category}".lower()

    if context.get("needs_24_7") == "Yes":
        route = "gap_analysis"
        reason = "Demo fallback selected gap_analysis because the user needs 24/7 access."
    elif any(word in text for word in ["verify", "phone", "website", "still open", "valid"]):
        route = "validation_review"
        reason = "Demo fallback selected validation_review based on validation-related language."
    elif any(word in text for word in ["email", "reach out", "contact", "provider"]):
        route = "outreach_email"
        reason = "Demo fallback selected outreach_email based on outreach language."
    elif any(word in text for word in ["tracker", "follow up", "follow-up", "called"]):
        route = "tracker_generation"
        reason = "Demo fallback selected tracker_generation based on follow-up language."
    elif any(word in text for word in ["policy", "gap", "failed", "barrier"]):
        route = "system_gap_brief"
        reason = "Demo fallback selected system_gap_brief based on system-gap language."
    else:
        route = "location_radius_match"
        reason = (
            "Demo fallback selected location_radius_match because the user provided a resource need and "
            "location/radius context."
        )

    return {
        "routing_mode": "DEMO FALLBACK - not a live LLM decision",
        "selected_route": route,
        "reason": reason,
        "confidence": "demo-only",
        "tool_used": "analyze_resource_gaps_and_build_contingency_plan",
    }


def llm_select_route(client, user_need, resource_category, primary_location, additional_locations, radius_miles, context):
    prompt = f"""
You are the LIFT Agent router.

LIFT means Locate. Identify. Follow-up. Track.

Choose exactly one route:
{json.dumps(ROUTES, indent=2)}

Route definitions:
- resource_match: user mainly needs matching resources.
- location_radius_match: location, distance, or multiple search areas matter.
- gap_analysis: barriers, eligibility, hours, transportation, or fit issues matter.
- validation_review: user needs to verify phone, website, hours, or resource status.
- outreach_email: user needs a provider outreach message.
- tracker_generation: user needs follow-up rows or action tracking.
- system_gap_brief: user needs a higher-level gap report.
- fallback_review: unclear request.

Return JSON only:
{{
  "selected_route": "...",
  "reason": "...",
  "confidence": "low/medium/high",
  "evidence": ["...", "..."],
  "tool_used": "analyze_resource_gaps_and_build_contingency_plan"
}}

User need:
{user_need}

Resource category:
{resource_category}

Primary location:
{primary_location}

Additional locations:
{additional_locations}

Radius miles:
{radius_miles}

Context:
{json.dumps(context, indent=2)}
"""

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": "You route resource navigation requests. Return valid JSON only."},
            {"role": "user", "content": prompt.strip()},
        ],
        temperature=0,
    )

    raw = response.choices[0].message.content or ""
    parsed = parse_json_safely(raw)

    selected_route = parsed.get("selected_route", "fallback_review")

    if selected_route not in ROUTES:
        selected_route = "fallback_review"

    return {
        "routing_mode": "LIVE LLM ROUTE DECISION",
        "router_model": DEFAULT_MODEL,
        "selected_route": selected_route,
        "reason": parsed.get("reason", "No reason returned."),
        "confidence": parsed.get("confidence", "unknown"),
        "evidence": parsed.get("evidence", []),
        "tool_used": "analyze_resource_gaps_and_build_contingency_plan",
        "raw_router_response": raw,
    }


def run_live_llm_tool_workflow(
    user_need,
    resource_category,
    primary_location,
    additional_locations,
    radius_miles,
    context,
    selected_outputs,
    resource_data,
    data_source_trace,
):
    client = get_openai_client()

    route_trace = llm_select_route(
        client=client,
        user_need=user_need,
        resource_category=resource_category,
        primary_location=primary_location,
        additional_locations=additional_locations,
        radius_miles=radius_miles,
        context=context,
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are LIFT Agent, an AI-assisted resource matching, gap review, outreach drafting, "
                "and follow-up tracking assistant. You must call the custom tool before writing the final response."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "user_need": user_need,
                    "resource_category": resource_category,
                    "primary_location": primary_location,
                    "additional_locations": additional_locations,
                    "radius_miles": radius_miles,
                    "context": context,
                    "selected_outputs": selected_outputs,
                    "route_trace": route_trace,
                    "external_data_trace": data_source_trace,
                },
                indent=2,
            ),
        },
    ]

    first_response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        tools=[ANALYZE_RESOURCE_GAP_TOOL, MCP_BASIC_PROVIDER_CHECK_TOOL],
        tool_choice={
            "type": "function",
            "function": {"name": "analyze_resource_gaps_and_build_contingency_plan"},
        },
        temperature=0.2,
    )

    first_message = first_response.choices[0].message
    tool_calls = first_message.tool_calls or []

    if not tool_calls:
        raise RuntimeError("The model did not request the custom tool.")

    messages.append(first_message.model_dump(exclude_none=True))

    tool_result = None

    for tool_call in tool_calls:
        # Support both the main analysis tool and the MCP provider check tool
        if tool_call.function.name == "analyze_resource_gaps_and_build_contingency_plan":
            arguments = parse_json_safely(tool_call.function.arguments)

            tool_result = analyze_resource_gaps_and_build_contingency_plan(
                user_need=arguments.get("user_need", user_need),
                resource_category=arguments.get("resource_category", resource_category),
                primary_location=arguments.get("primary_location", primary_location),
                additional_locations=arguments.get("additional_locations", additional_locations),
                radius_miles=arguments.get("radius_miles", radius_miles),
                context=arguments.get("context", context),
                selected_outputs=arguments.get("selected_outputs", selected_outputs),
                resource_data=resource_data,
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result, indent=2),
                }
            )

        elif tool_call.function.name == "mcp_basic_provider_check":
            arguments = parse_json_safely(tool_call.function.arguments)

            mcp_result = mcp_basic_provider_check(
                provider_name=arguments.get("provider_name", ""),
                website_url=arguments.get("website_url", ""),
                category=arguments.get("category"),
                location=arguments.get("location"),
                user_need=arguments.get("user_need"),
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(mcp_result, indent=2),
                }
            )

        else:
            raise RuntimeError(f"Unexpected tool requested: {tool_call.function.name}")

    final_instruction = f"""
Write a concise structured report using the tool result.
Use this display language when possible: {context.get("display_language", "English")}.
If language access was requested, mention that provider language support must be confirmed: {context.get("language_access_needed", "No preference")}.
Include:
1. Best-fit resource summary
2. Main access/eligibility gaps
3. Three contingency options
4. Outreach draft note
5. Tracker next steps
6. System gap note

Do not claim real-world verification. State that public search results still require direct provider confirmation.
State that the resource list came from this external data trace unless fallback_used is true: {json.dumps(data_source_trace, indent=2)}.
Use these local curated-corpus citations when they support the recommendation: {json.dumps(context.get("retrieval_trace", {}), indent=2)}.
"""

    messages.append({"role": "user", "content": final_instruction.strip()})

    final_response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=0.3,
    )

    final_text = final_response.choices[0].message.content or ""

    tool_trace = {
        "tool_requested_by_model": True,
        "tool_name": "analyze_resource_gaps_and_build_contingency_plan",
        "tool_mode": "OpenAI model-callable function tool",
        "external_data_source": data_source_trace,
        "tool_result_keys": list(tool_result.keys()) if tool_result else [],
        "retrieval_trace": context.get("retrieval_trace", {}),
    }

    return final_text, route_trace, tool_trace, tool_result


def build_demo_report(tool_result, route_trace):
    lines = [
        "## LIFT Resource Plan",
        "",
        f"**Recommended first resource:** {tool_result.get('recommended_first_resource', 'No recommendation available')}",
        "",
        "### Why this route was selected",
        f"- {route_trace.get('reason')}",
        "",
        "### Main fit and gap concerns",
    ]

    for item in (
        tool_result.get("fit_concerns", [])
        + tool_result.get("eligibility_barriers", [])
        + tool_result.get("access_barriers", [])
        + tool_result.get("twenty_four_seven_gaps", [])
        + tool_result.get("validation_flags", [])
    ):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("### Three contingency options")

    for plan in tool_result.get("contingency_plans", []):
        lines.append(f"**{plan['plan']}: {plan['title']}**")
        for step in plan["steps"]:
            lines.append(f"- {step}")
        lines.append("")

    lines.append("### User-approved outreach draft")
    lines.append("This is a draft only. Nothing is sent automatically.")
    lines.append("")
    lines.append("```text")
    lines.append(tool_result.get("outreach_email_draft", ""))
    lines.append("```")
    lines.append("")
    lines.append("### System gap notes")

    for note in tool_result.get("system_gap_notes", []):
        lines.append(f"- {note}")

    if tool_result.get("citations"):
        lines.append("")
        lines.append("### Curated corpus citations")
        for citation in tool_result.get("citations", []):
            lines.append(f"- [{citation}] Local LIFT curated guidance")

    return "\n".join(lines)


def init_session_state():
    """Initialize required session state variables for consent and privacy."""
    for key in [
        "consent_public_data",
        "consent_outputs",
        "consent_no_phone",
        "consent_agent_actions",
        "consent_email_review",
    ]:
        if key not in st.session_state:
            st.session_state[key] = False
    if "privacy_session_only" not in st.session_state:
        st.session_state["privacy_session_only"] = True
    if "privacy_include_notes" not in st.session_state:
        st.session_state["privacy_include_notes"] = True
    if "privacy_allow_website_checks" not in st.session_state:
        st.session_state["privacy_allow_website_checks"] = True
    if "language" not in st.session_state:
        st.session_state["language"] = "English"
    if "language_access_needed" not in st.session_state:
        st.session_state["language_access_needed"] = "No preference"
    if "optional_context" not in st.session_state:
        st.session_state["optional_context"] = []
    if "case_history" not in st.session_state:
        st.session_state["case_history"] = []
    if "current_case_record" not in st.session_state:
        st.session_state["current_case_record"] = {}
    if "need_text" not in st.session_state:
        st.session_state["need_text"] = ""
    if "agent_activity_log" not in st.session_state:
        st.session_state["agent_activity_log"] = []


def render_privacy_consent_section():
    """Render the Privacy, Consent, and User Control section."""
    st.subheader("Required Consent Before Agent Actions")
    labels = [
        ("consent_public_data", "I understand LIFT uses public resource data and provider website checks when available."),
        ("consent_outputs", "I understand LIFT may generate outreach drafts, tracker rows, and mapped provider results."),
        ("consent_no_phone", "I understand LIFT will not call providers or monitor voicemail."),
        ("consent_agent_actions", "I approve LIFT to perform the selected agent actions."),
        ("consent_email_review", "I understand any email must be reviewed and approved before sending."),
    ]
    for key, label in labels:
        st.session_state[key] = st.checkbox(label, value=st.session_state.get(key, False), key=f"{key}_check")

    all_consents_checked = all(st.session_state.get(key, False) for key, _ in labels)

    st.markdown("**Privacy Settings**")
    st.markdown(
        """
- Session-only output history: On
- Include privacy and consent notes in generated plan: On
- Allow basic public provider website checks: On
"""
    )
    st.session_state["privacy_session_only"] = True
    st.session_state["privacy_include_notes"] = True
    st.session_state["privacy_allow_website_checks"] = True

    if not all_consents_checked:
        st.info("Check all required consent boxes to enable Generate LIFT Plan.")
    return all_consents_checked

    st.header(t("Privacy, Consent, and User Control"))
    
    st.markdown(
        """
**LIFT Agent uses public external search data when available, with clearly labeled fallback data if a specific external action is unavailable.**
LIFT can send approved SMTP email only after human review. LIFT does not call providers, monitor voicemail, or scan inboxes.
        """
    )
    
    st.subheader("Required Consent Checkboxes")
    st.markdown("**All of the following must be checked before you can generate a LIFT plan:**")
    
    col1, col2 = st.columns([0.05, 0.95])
    with col1:
        st.write("")
    with col2:
        st.session_state["consent_synthetic_data"] = st.checkbox(
            "I understand LIFT uses public external search data or clearly labeled fallback information when needed.",
            value=st.session_state.get("consent_synthetic_data", False),
            key="consent_synthetic_check"
        )
    
    col1, col2 = st.columns([0.05, 0.95])
    with col1:
        st.write("")
    with col2:
        st.session_state["consent_no_sensitive_data"] = st.checkbox(
            "I will not enter private, classified, restricted, protected, or sensitive personal information.",
            value=st.session_state.get("consent_no_sensitive_data", False),
            key="consent_no_sensitive_check"
        )
    
    col1, col2 = st.columns([0.05, 0.95])
    with col1:
        st.write("")
    with col2:
        st.session_state["consent_no_automation"] = st.checkbox(
            "I understand LIFT does not call providers, monitor voicemail, or scan inboxes.",
            value=st.session_state.get("consent_no_automation", False),
            key="consent_no_automation_check"
        )
    
    col1, col2 = st.columns([0.05, 0.95])
    with col1:
        st.write("")
    with col2:
        st.session_state["consent_human_approval"] = st.checkbox(
            "I understand AI-generated outreach must be reviewed and approved by a human before use.",
            value=st.session_state.get("consent_human_approval", False),
            key="consent_human_approval_check"
        )
    
    all_consents_checked = (
        st.session_state.get("consent_synthetic_data", False)
        and st.session_state.get("consent_no_sensitive_data", False)
        and st.session_state.get("consent_no_automation", False)
        and st.session_state.get("consent_human_approval", False)
    )
    
    if not all_consents_checked:
        st.warning("⚠️ **Please check all required boxes above before generating a LIFT plan.**")
    
    st.subheader("Optional Privacy Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state["privacy_session_only"] = st.checkbox(
            "Use session-only output history (do not save to disk)",
            value=st.session_state.get("privacy_session_only", False),
            key="privacy_session_only_check"
        )
    
    with col2:
        st.session_state["privacy_include_notes"] = st.checkbox(
            "Include privacy and consent notes in generated plan",
            value=st.session_state.get("privacy_include_notes", True),
            key="privacy_include_notes_check"
        )
    
    st.session_state["privacy_allow_website_checks"] = st.checkbox(
        "Allow basic public provider website checks if available",
        value=st.session_state.get("privacy_allow_website_checks", True),
        key="privacy_allow_website_checks_check"
    )
    
    return all_consents_checked


def render_privacy_notice():
    st.info(
        "Use public information only. Do not enter private, classified, restricted, protected, "
        "or sensitive information. LIFT can send approved SMTP email only after review. "
        "LIFT does not call providers, monitor voicemail, or scan inboxes."
    )


def render_generate_page():
    language = current_language()
    language_access_needed = st.session_state.get("language_access_needed", "No preference")

    st.markdown(
        "LIFT Agent is a human-supervised autonomous resource navigation agent. It can search public provider information, "
        "check provider websites, generate mapped results, create outreach drafts, send approved emails through SMTP, and "
        "build follow-up tracker rows. LIFT does not place phone calls; phone calls remain a user action, but LIFT prepares "
        "the call plan and script."
    )

    st.header("1. Tell LIFT what you need")
    st.caption("Optional details only. You can write messy. LIFT will organize it.")

    examples = [
        "Food pantry near me",
        "Emergency shelter",
        "Help with utility bill",
        "Transportation to appointments",
        "Veteran housing support",
        "Legal aid",
        "Childcare help",
    ]
    chip_cols = st.columns(4)
    for idx, example in enumerate(examples):
        with chip_cols[idx % 4]:
            if st.button(example, key=f"need_chip_{idx}", width="stretch"):
                st.session_state["need_text"] = example

    user_need = st.text_area(
        "What do you need help with?",
        key="need_text",
        placeholder="Example: I need a food pantry near Grand Rapids, but I work third shift and have limited transportation.",
        height=118,
    )
    st.session_state["user_need"] = user_need

    intake_cols = st.columns([1, 1])
    with intake_cols[0]:
        resource_category = st.selectbox(
            get_text("Resource category", language),
            [
                "Any / Not Sure",
                "Food / Basic Needs",
                "Housing / Utilities",
                "Financial Assistance",
                "Transportation",
                "Legal / Administrative",
                "Behavioral Health",
                "Emergency / 24-7 Crisis",
                "Veteran / Service Member Support",
                "Family Readiness / FRG",
                "General Support / 24-7 Navigation",
            ],
        )
    with intake_cols[1]:
        urgency = st.selectbox(get_text("Urgency", language), ["Routine", "Soon", "Urgent", "Crisis / immediate"])

    st.header("2. Where should LIFT look?")
    loc_col1, loc_col2, loc_col3 = st.columns(3)
    with loc_col1:
        primary_location = st.text_input(
            get_text("Primary search location", language),
            value=st.session_state.get("primary_location", "Grand Rapids, MI"),
            key="primary_location",
        )
    with loc_col2:
        additional_locations_text = st.text_input(
            get_text("Additional locations", language),
            value=st.session_state.get("additional_locations_text", "East Lansing, MI"),
            placeholder="East Lansing, MI",
            key="additional_locations_text",
        )
    with loc_col3:
        radius_miles = st.slider(
            get_text("Search radius in miles", language),
            5,
            100,
            st.session_state.get("radius_miles", 25),
            step=5,
            key="radius_miles",
        )

    additional_locations = [
        item.strip()
        for item in additional_locations_text.replace(",", ";").split(";")
        if item.strip()
    ]

    access_col1, access_col2 = st.columns(2)
    with access_col1:
        transportation = st.selectbox(
            "Transportation limits",
            [
                "No",
                "Limited",
                "Public transportation only",
                "Walking only",
                "Ride share only",
                "I have transportation",
                "Not sure",
            ],
            key="transportation_limits",
        )
    with access_col2:
        access_modes = st.multiselect(
            "Preferred access",
            ["Nearby", "Online", "Phone", "Walk-in", "Appointment", "24/7 or after-hours", "No preference"],
            default=st.session_state.get("preferred_access", ["Nearby", "Online"]),
            key="preferred_access",
        )

    additional_preview = ", ".join(additional_locations) if additional_locations else "no additional locations"
    preferred_preview = " and ".join(access_modes) if access_modes else "No preference"
    st.markdown(
        f"""
        <div class="lift-preview-card">
            <strong style="color:#0E5F73;">Search area preview</strong>
            <div style="margin-top:0.3rem;color:#24302F;">
                LIFT will start near {primary_location or 'Grand Rapids, MI'} and also consider {additional_preview}
                within {radius_miles} miles where appropriate. Transportation limit: {transportation}.
                Preferred access: {preferred_preview}.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.header("3. Access barriers and fit")
    c1, c2, c3 = st.columns(3)
    with c1:
        audience = st.selectbox(
            "User type",
            [
                "Active-duty service member",
                "National Guard member",
                "Reservist",
                "Veteran",
                "Military spouse or partner",
                "Military-connected family",
                "Surviving spouse or family member",
                "Caregiver",
                "Dependent",
                "Parent or guardian",
                "Student",
                "Senior",
                "Person with a disability",
                "Unhoused or housing unstable",
                "Justice-impacted / reentry",
                "Community member",
                "Not sure",
                "Other",
            ],
        )
    with c2:
        language_access_needed = st.selectbox(
            "Language support needed",
            ["No preference", "English", "Spanish", "Italian", "Other / Interpreter needed"],
            index=0,
            key="main_language_need_select",
        )
        st.session_state["language_access_needed"] = language_access_needed
    with c3:
        needs_24_7 = st.selectbox("Needs 24/7 or after-hours option?", ["No", "Yes", "Not sure"])
    barrier_cols = st.columns(3)
    with barrier_cols[0]:
        free_low_cost = st.checkbox("Free or low-cost only", value=True)
        appointment_okay = st.checkbox("Appointment required is okay", value=True)
    with barrier_cols[1]:
        documents_available = "No" if st.checkbox("Documentation concerns", value=False) else "Yes"
        eligibility_concerns = st.checkbox("Eligibility concerns", value=False)
    with barrier_cols[2]:
        accessibility_barriers = st.checkbox("Accessibility or transportation barriers", value=(transportation != "I have transportation"))

    with st.container(border=True):
        st.markdown("**Optional: Add contact info, files, or links**")
        st.caption(
            "Uploads and links are optional. LIFT uses them only to improve this session's plan. "
            "Do not upload classified, restricted, or highly sensitive personal information."
        )
        contact_cols = st.columns(2)
        with contact_cols[0]:
            user_email = st.text_input("User email address, optional", key="optional_user_email")
            preferred_contact_method = st.selectbox(
                "Preferred contact method, optional",
                ["Not sure", "Email", "Phone call by user", "Text message by user", "Print/save only"],
                key="preferred_contact_method",
            )
            outreach_language = st.text_input("Preferred outreach language, optional", key="preferred_outreach_language")
        with contact_cols[1]:
            best_contact_time = st.text_input("Best time to contact providers, optional", key="best_contact_time")
            include_email_in_drafts = st.checkbox(
                "Include my email address in outreach drafts.",
                value=False,
                key="include_email_in_drafts",
            )
            supporting_links_text = st.text_area(
                "Paste optional links, such as a Google Drive, Google Doc, website, or resource list link",
                key="supporting_links_text",
                height=92,
            )
        notes_from_user_context = st.text_area("Anything else LIFT should know?", key="notes_from_user_context", height=95)
        uploaded_files = st.file_uploader(
            "Upload optional supporting files or photos",
            type=["pdf", "txt", "csv", "docx", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="supporting_uploads",
        )
        if uploaded_files:
            st.caption(
                "Uploaded file names/types are used as session context. LIFT does not claim full file or photo understanding in this version."
            )
            for uploaded_file in uploaded_files:
                st.write(f"- {uploaded_file.name} ({uploaded_file.type or 'unknown type'})")
        st.caption("Google Drive or Google Docs links are stored as reference links only unless a future authenticated Google Drive integration is added.")

    context = {
        "audience": audience,
        "transportation": transportation,
        "needs_24_7": needs_24_7,
        "documents_available": documents_available,
        "urgency": urgency,
        "display_language": language,
        "language_access_needed": language_access_needed,
        "access_modes": access_modes,
        "free_low_cost": free_low_cost,
        "appointment_okay": appointment_okay,
        "eligibility_concerns": eligibility_concerns,
        "accessibility_barriers": accessibility_barriers,
        "user_preferred_contact_method": preferred_contact_method,
        "user_outreach_language": outreach_language,
        "user_email_provided": "yes" if user_email.strip() else "no",
        "include_user_email_in_drafts": include_email_in_drafts,
        "best_contact_time": best_contact_time,
        "supporting_files_count": len(uploaded_files or []),
        "supporting_file_names": [uploaded_file.name for uploaded_file in uploaded_files or []],
        "supporting_links": [line.strip() for line in supporting_links_text.splitlines() if line.strip()],
        "notes_from_user_context": notes_from_user_context,
    }

    with st.expander(get_text("Optional Context", language), expanded=False):
        st.caption(get_text("Select only what you are comfortable sharing. This helps match better resources.", language))
        optional_labels = [
            "Veteran",
            "Disabled Veteran",
            "Military family",
            "Single parent",
            "Parent/caregiver",
            "Pregnant/postpartum",
            "Student",
            "Senior",
            "Youth/young adult",
            "Housing unstable",
            "No transportation",
            "Low/no income",
            "Uninsured",
            "Food insecure",
            "Legal help",
            "Reentry support",
            "Spanish services",
            "LGBTQIA+ affirming",
            "Disability resources",
            "After-hours services",
        ]
        selected_optional = []
        opt_cols = st.columns(3)
        for idx, label in enumerate(optional_labels):
            if opt_cols[idx % 3].checkbox(label, key=f"guided_optctx_{idx}"):
                selected_optional.append(label)
    st.session_state["optional_context"] = selected_optional
    context["optional_context"] = selected_optional

    st.header("4. Choose agent actions")
    st.subheader("Meet your LIFT Guides")
    st.markdown("You can choose one guide or let several guides work together on your LIFT plan.")
    guide_cards = [
        ("Lia", "the main LIFT guide", "Hi, I'm Lia. I'll help organize what you need and guide you through your LIFT plan.", []),
        ("Scout", "Locate", "I help find public provider options based on your need and location.", ["Search public provider options", "Check provider websites", "Show Google map"]),
        ("Ivy", "Identify", "I help notice barriers early so your plan is more realistic and useful.", ["Create resource fit summary", "Identify barriers and gaps", "Create three backup options"]),
        ("Ember", "Follow-up", "I help prepare outreach drafts and call scripts you can review and use.", ["Generate email draft", "Generate call script"]),
        ("Tally", "Track", "I help track your next steps so nothing gets lost.", ["Create tracker rows", "Create CSV tracker download"]),
    ]
    guide_cols = st.columns(5)
    for idx, (name, role, description, actions) in enumerate(guide_cards):
        with guide_cols[idx]:
            action_text = "<br>".join(actions) if actions else "Guides the full plan"
            st.markdown(
                f"""
                <div class="lift-guide-card">
                    <div class="lift-guide-portrait">{name[0]}</div>
                    <div class="lift-guide-name">{name}</div>
                    <div class="lift-guide-role">{role}</div>
                    <div class="lift-guide-desc">{description}</div>
                    <div class="lift-guide-actions">{action_text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Choose {name}", key=f"guide_{name.lower()}", width="stretch"):
                if name == "Scout":
                    for key in ["act_search", "act_websites", "act_map"]:
                        st.session_state[key] = True
                elif name == "Ivy":
                    for key in ["act_fit", "act_gaps", "act_backup"]:
                        st.session_state[key] = True
                elif name == "Ember":
                    for key in ["act_email", "act_call"]:
                        st.session_state[key] = True
                elif name == "Tally":
                    for key in ["act_tracker", "act_csv"]:
                        st.session_state[key] = True
                else:
                    for key in ["act_search", "act_websites", "act_map", "act_fit", "act_gaps", "act_backup", "act_email", "act_call", "act_tracker", "act_csv"]:
                        st.session_state[key] = True
                st.rerun()

    quick_cols = st.columns(5)
    quick_picks = [
        ("Help me choose", ["act_search", "act_websites", "act_map", "act_fit", "act_gaps", "act_backup", "act_email", "act_call", "act_tracker", "act_csv"]),
        ("I want to find resources", ["act_search", "act_websites", "act_map"]),
        ("I need help planning", ["act_fit", "act_gaps", "act_backup"]),
        ("I want outreach help", ["act_email", "act_call"]),
        ("I need help staying organized", ["act_tracker", "act_csv"]),
    ]
    for idx, (label, keys) in enumerate(quick_picks):
        with quick_cols[idx]:
            if st.button(label, key=f"quick_pick_{idx}", width="stretch"):
                for key in keys:
                    st.session_state[key] = True
                st.rerun()

    st.caption("Choose what LIFT should do:")
    action_cols = st.columns(3)
    with action_cols[0]:
        st.markdown("**Find**")
        act_search = st.checkbox("Search public provider options", value=True, key="act_search")
        act_websites = st.checkbox("Check provider websites", value=True, key="act_websites")
        act_map = st.checkbox("Show Google map", value=True, key="act_map")
    with action_cols[1]:
        st.markdown("**Plan**")
        act_fit = st.checkbox("Create resource fit summary", value=True, key="act_fit")
        act_gaps = st.checkbox("Identify barriers and gaps", value=True, key="act_gaps")
        act_backup = st.checkbox("Create three backup options", value=True, key="act_backup")
    with action_cols[2]:
        st.markdown("**Follow up**")
        act_email = st.checkbox("Generate email draft", value=True, key="act_email")
        act_call = st.checkbox("Generate call script", value=True, key="act_call")
        act_tracker = st.checkbox("Create tracker rows", value=True, key="act_tracker")
        act_csv = st.checkbox("Create CSV tracker download", value=True, key="act_csv")
        act_smtp = st.checkbox("Send approved email by SMTP", value=False, key="act_smtp")

    selected_outputs = []
    if act_fit:
        selected_outputs.append("Resource fit summary")
    if act_gaps:
        selected_outputs.append("Gap analysis")
    if act_backup:
        selected_outputs.append("Three contingency plans")
    if act_email:
        selected_outputs.append("User-approved outreach draft")
    if act_tracker:
        selected_outputs.append("Tracker rows")
    if act_map:
        selected_outputs.append("Map view")
    if act_csv:
        selected_outputs.append("CSV tracker download")

    all_consents_checked = render_privacy_consent_section()

    api_key = get_openai_api_key()
    if not api_key:
        st.info("OPENAI_API_KEY is not configured. LIFT will still run the local agent workflow and label any fallback data.")
    if act_map and not google_maps_key_present():
        st.info("GOOGLE_MAPS_API_KEY is not configured. Google geocoding will be skipped; existing public-search coordinates may still be shown when available.")
    if act_smtp:
        smtp_missing = [
            name
            for name in ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM"]
            if not get_secret_or_env(name)
        ]
        if smtp_missing:
            st.info("SMTP email sending is selected but not configured. Missing: " + ", ".join(smtp_missing))

    generate = st.button(
        get_text("Generate LIFT Plan", language),
        type="primary",
        width="stretch",
        disabled=not all_consents_checked,
    )

    if generate:
        if not user_need.strip():
            st.error("Enter a resource need first.")
            st.stop()

        input_errors, input_warnings = validate_user_input(user_need)
        for warning in input_warnings:
            st.warning(warning)
        if input_errors:
            for input_error in input_errors:
                st.error(input_error)
            st.stop()

        agent_log = []
        log_agent_action(agent_log, "User need received", "completed", "local/session data", "The guided intake was submitted.")
        log_agent_action(agent_log, "Primary location received", "completed", "local/session data", "Primary search location was received from Step 2.")
        log_agent_action(
            agent_log,
            "Additional locations received/skipped",
            "completed" if additional_locations else "skipped",
            "local/session data",
            f"{len(additional_locations)} additional location(s) received." if additional_locations else "No additional locations were provided.",
        )
        log_agent_action(agent_log, "Search radius received", "completed", "local/session data", f"Search radius received: {radius_miles} miles.")
        log_agent_action(agent_log, "Transportation limits received", "completed", "local/session data", f"Transportation limit received: {transportation}.")
        log_agent_action(agent_log, "Preferred access received", "completed", "local/session data", f"Preferred access received: {', '.join(access_modes) if access_modes else 'No preference'}.")
        log_agent_action(
            agent_log,
            "Optional contact info received",
            "completed" if any([user_email.strip(), preferred_contact_method != "Not sure", outreach_language.strip(), best_contact_time.strip()]) else "skipped",
            "local/session data",
            "Optional contact preferences were received." if any([user_email.strip(), preferred_contact_method != "Not sure", outreach_language.strip(), best_contact_time.strip()]) else "No optional contact preferences were provided.",
        )
        log_agent_action(
            agent_log,
            "Additional context received",
            "completed" if notes_from_user_context.strip() else "skipped",
            "local/session data",
            "Additional user context notes were received." if notes_from_user_context.strip() else "No additional context notes were provided.",
        )
        log_agent_action(
            agent_log,
            "File upload received",
            "completed" if uploaded_files else "skipped",
            "local/session data",
            f"{len(uploaded_files or [])} optional file(s) attached for this session." if uploaded_files else "No optional files were uploaded.",
        )
        supporting_links = context.get("supporting_links", [])
        log_agent_action(
            agent_log,
            "Link reference received",
            "completed" if supporting_links else "skipped",
            "local/session data",
            f"{len(supporting_links)} optional link reference(s) stored for this session." if supporting_links else "No optional links were provided.",
        )
        search_geocode_trace = geocode_search_locations(primary_location, additional_locations, agent_log)
        st.session_state["search_area_geocode_trace"] = search_geocode_trace
        st.session_state["geocoded_search_locations"] = [
            item for item in search_geocode_trace.get("locations", []) if item.get("status") == "completed"
        ]
        emergency_terms = [
            "immediate danger",
            "self-harm",
            "suicide",
            "kill myself",
            "violence",
            "medical emergency",
            "overdose",
            "unsafe right now",
        ]
        emergency_notice = any(term in user_need.lower() for term in emergency_terms) or urgency == "Crisis / immediate"
        if emergency_notice:
            log_agent_action(
                agent_log,
                "Crisis safety notice prepared",
                "completed",
                "local/session data",
                "LIFT is not an emergency service; emergency and crisis language will be shown before planning outputs.",
            )

        retrieval_trace = retrieve_curated_context(
            user_need=user_need,
            resource_category=resource_category,
            context=context,
        )
        context["retrieval_trace"] = retrieval_trace

        interpreted_intent = infer_intent_fallback(
            user_need=user_need,
            resource_category=resource_category,
            primary_location=primary_location,
            context=context,
        )
        if api_key and OPENAI_AVAILABLE:
            try:
                interpreted_intent = llm_interpret_request(
                    client=get_openai_client(),
                    user_need=user_need,
                    resource_category=resource_category,
                    primary_location=primary_location,
                    additional_locations=additional_locations,
                    radius_miles=radius_miles,
                    context=context,
                )
                log_agent_action(agent_log, "Fit and intent interpreted", "completed", "real external API/tool data", "OpenAI interpretation completed.")
            except Exception as error:
                interpreted_intent["interpretation_warning"] = f"Live LLM interpretation failed; fallback interpretation used: {type(error).__name__}"
                log_agent_action(agent_log, "Fit and intent interpreted", "fallback used", "local/session data", interpreted_intent["interpretation_warning"])
        else:
            log_agent_action(agent_log, "Fit and intent interpreted", "fallback used", "local/session data", "Local interpretation used because OPENAI_API_KEY is unavailable.")

        context["interpreted_intent"] = interpreted_intent
        effective_resource_category = resource_category
        if resource_category == "Any / Not Sure" and interpreted_intent.get("need_type") in [
            "Food / Basic Needs",
            "Housing / Utilities",
            "Financial Assistance",
            "Transportation",
            "Legal / Administrative",
            "Behavioral Health",
            "Emergency / 24-7 Crisis",
            "Veteran / Service Member Support",
            "Family Readiness / FRG",
            "General Support / 24-7 Navigation",
        ]:
            effective_resource_category = interpreted_intent["need_type"]

        if act_search:
            resources_df, data_source_trace = search_public_resources(
                user_need,
                effective_resource_category,
                primary_location,
                additional_locations,
                radius_miles,
                agent_log,
            )
        else:
            resources_df = pd.DataFrame(synthetic_resource_data())
            data_source_trace = {"data_source": "Local fallback examples", "fallback_used": True, "result_count": len(resources_df)}
            log_agent_action(agent_log, "Public resource search started", "skipped", "local/session data", "User did not select public provider search.")

        resource_data = resources_df.to_dict(orient="records")

        with st.spinner("Running LIFT agent actions..."):
            if api_key and OPENAI_AVAILABLE:
                try:
                    final_text, route_trace, tool_trace, tool_result = run_live_llm_tool_workflow(
                        user_need=user_need,
                        resource_category=effective_resource_category,
                        primary_location=primary_location,
                        additional_locations=additional_locations,
                        radius_miles=radius_miles,
                        context=context,
                        selected_outputs=selected_outputs,
                        resource_data=resource_data,
                        data_source_trace=data_source_trace,
                    )
                    log_agent_action(agent_log, "Fit and gap analysis completed", "completed", "real external API/tool data", "OpenAI tool workflow completed.")
                except Exception as error:
                    route_trace = demo_route_decision(user_need, effective_resource_category, context)
                    tool_result = analyze_resource_gaps_and_build_contingency_plan(
                        user_need,
                        effective_resource_category,
                        primary_location,
                        additional_locations,
                        radius_miles,
                        context,
                        selected_outputs,
                        resource_data,
                    )
                    tool_trace = {"tool_name": "analyze_resource_gaps_and_build_contingency_plan", "tool_mode": "Local fallback after live workflow failure"}
                    final_text = build_demo_report(tool_result, route_trace)
                    log_agent_action(agent_log, "Fit and gap analysis completed", "fallback used", "local/session data", f"Live workflow failed: {type(error).__name__}")
            else:
                route_trace = demo_route_decision(user_need, effective_resource_category, context)
                tool_result = analyze_resource_gaps_and_build_contingency_plan(
                    user_need,
                    effective_resource_category,
                    primary_location,
                    additional_locations,
                    radius_miles,
                    context,
                    selected_outputs,
                    resource_data,
                )
                tool_trace = {"tool_name": "analyze_resource_gaps_and_build_contingency_plan", "tool_mode": "Local agent workflow"}
                final_text = build_demo_report(tool_result, route_trace)
                log_agent_action(agent_log, "Fit and gap analysis completed", "completed", "local/session data", "Local LIFT tool created fit, gap, backup, outreach, and tracker outputs.")

            provider_records = tool_result.get("matched_resources", [])
            provider_checks = []
            if act_websites:
                for provider in provider_records[:5]:
                    provider_checks.append(check_provider_website(provider, agent_log))
            else:
                log_agent_action(agent_log, "Provider websites checked", "skipped", "local/session data", "User did not select provider website checks.")

            if act_map:
                mapped_providers, geocode_trace = geocode_provider_locations(provider_records, agent_log)
                map_rows = render_google_map(mapped_providers, agent_log)
                tool_result["matched_resources"] = mapped_providers
            else:
                geocode_trace = {"configured": google_maps_key_present(), "geocoded_count": 0, "errors": []}
                map_rows = []
                log_agent_action(agent_log, "Google map generated", "skipped", "local/session data", "User did not select map output.")

            if act_email:
                first_provider = tool_result.get("matched_resources", [{}])[0] if tool_result.get("matched_resources") else {}
                email_draft = generate_outreach_email(user_need, first_provider, language_access_needed)
                if include_email_in_drafts and user_email.strip():
                    email_draft["body"] += f"\n\nPreferred reply email: {user_email.strip()}"
                tool_result["smtp_email_draft"] = email_draft
                log_agent_action(
                    agent_log,
                    "Outreach email draft created",
                    "completed",
                    "local/session data",
                    "Editable outreach draft prepared for human review.",
                    human_approval_required=True,
                )
            else:
                tool_result["smtp_email_draft"] = {"recipient": "", "subject": "", "body": ""}
                log_agent_action(agent_log, "Outreach email draft created", "skipped", "local/session data", "User did not select email draft generation.")

            if act_call:
                first_provider = tool_result.get("matched_resources", [{}])[0] if tool_result.get("matched_resources") else {}
                tool_result["call_script"] = generate_call_script(user_need, first_provider, language_access_needed)
                log_agent_action(agent_log, "Call script created", "completed", "local/session data", "Manual phone-call script prepared. LIFT did not call providers.")
            else:
                tool_result["call_script"] = ""
                log_agent_action(agent_log, "Call script created", "skipped", "local/session data", "User did not select call script generation.")

            if act_tracker:
                create_tracker_rows(tool_result, agent_log)
                add_optional_context_to_tracker_rows(tool_result, context)
            else:
                tool_result["tracker_rows"] = []
                log_agent_action(agent_log, "Tracker rows created", "skipped", "local/session data", "User did not select tracker rows.")

            if act_csv:
                tool_result["tracker_csv"] = export_tracker_csv(tool_result.get("tracker_rows", []), agent_log)
            else:
                tool_result["tracker_csv"] = ""
                log_agent_action(agent_log, "CSV tracker export created", "skipped", "local/session data", "User did not select CSV tracker export.")

            check_by_name = {check.get("provider_name"): check for check in provider_checks}
            for provider in tool_result.get("matched_resources", []):
                check = check_by_name.get(provider.get("resource_name"))
                if check:
                    provider["website_status"] = check.get("website_status", "unknown")
                    provider["website_check_confidence"] = check.get("confidence", "unknown")
                confidence, confidence_reason = provider_confidence_label(
                    provider,
                    check=check,
                    fallback_used=data_source_trace.get("fallback_used", False),
                )
                provider["public_service_category"] = classify_provider_category(provider)
                provider["confidence_label"] = confidence
                provider["confidence_reason"] = confidence_reason
                provider["next_best_action"] = next_best_provider_action(provider, confidence)
                if provider.get("lat") not in ["", None] and provider.get("lon") not in ["", None] and not provider.get("map_link"):
                    provider["map_link"] = f"https://www.google.com/maps/search/?api=1&query={provider.get('lat')},{provider.get('lon')}"

            map_summary = build_map_summary(
                tool_result.get("matched_resources", []),
                provider_checks,
                map_rows,
                radius_miles,
            )
            log_agent_action(
                agent_log,
                "Map summary prepared",
                "completed" if map_rows or tool_result.get("matched_resources") else "skipped",
                "local/session data",
                "Executive map summary card prepared from provider and map rows.",
            )

            log_agent_action(
                agent_log,
                "SMTP email sending",
                "skipped",
                "local/session data",
                "SMTP email is only sent from the review panel after explicit approval.",
                human_approval_required=True,
            )
            write_agent_audit_log(agent_log)

            st.session_state["route_trace"] = route_trace
            st.session_state["tool_trace"] = tool_trace
            st.session_state["tool_result"] = tool_result
            st.session_state["data_source_trace"] = data_source_trace
            st.session_state["retrieval_trace"] = retrieval_trace
            st.session_state["interpreted_intent"] = interpreted_intent
            st.session_state["provider_checks"] = provider_checks
            st.session_state["map_rows"] = map_rows
            st.session_state["geocode_trace"] = geocode_trace
            st.session_state["map_summary"] = map_summary
            st.session_state["emergency_notice"] = emergency_notice
            st.session_state["final_text"] = final_text
            st.session_state["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if st.session_state.get("tool_result"):
        st.divider()
        st.header("Results")
        translation_safety_note()
        if st.session_state.get("emergency_notice"):
            st.warning(
                "LIFT is not an emergency service. If there is immediate danger, call emergency services or a local crisis line. "
                "LIFT can still help organize non-emergency follow-up resources."
            )

        log_df = pd.DataFrame(st.session_state.get("agent_activity_log", []))
        with st.container(border=True):
            st.subheader("Agent Activity Log")
            if not log_df.empty:
                st.dataframe(
                    log_df[["timestamp", "action", "status", "data_source", "human_approval_required", "message"]],
                    width="stretch",
                )

        tool_result = st.session_state["tool_result"]
        matched_df = pd.DataFrame(tool_result.get("matched_resources", []))

        with st.container(border=True):
            st.subheader("Top 3 Recommended Next Steps")
            top_steps = []
            if tool_result.get("recommended_first_resource"):
                top_steps.append(f"Start with {tool_result.get('recommended_first_resource')} and confirm current hours, eligibility, and intake steps.")
            for provider in tool_result.get("matched_resources", [])[:2]:
                action = provider.get("next_best_action")
                if action:
                    top_steps.append(f"{provider.get('resource_name', 'Provider')}: {action}")
            while len(top_steps) < 3:
                top_steps.append("Use the tracker to record what was confirmed, what failed, and the next follow-up date.")
            for step in top_steps[:3]:
                st.markdown(f"- {step}")

        with st.container(border=True):
            st.subheader("Resource Fit Summary")
            st.write(f"Best place to start: **{tool_result.get('recommended_first_resource', 'No match yet')}**")
            for item in tool_result.get("fit_concerns", []):
                st.markdown(f"- {item}")

        with st.container(border=True):
            st.subheader("Provider Options")
            if matched_df.empty:
                st.info("No provider options were prepared.")
            else:
                display_cols = [
                    col
                    for col in [
                        "resource_name",
                        "category",
                        "city",
                        "business_hours",
                        "phone",
                        "group_email",
                        "website",
                        "eligibility",
                        "status",
                        "distance_miles",
                        "lat",
                        "lon",
                        "geocoding_status",
                        "map_link",
                        "confidence_label",
                        "next_best_action",
                    ]
                    if col in matched_df.columns
                ]
                st.dataframe(matched_df[display_cols], width="stretch")
                for idx, provider in enumerate(tool_result.get("matched_resources", [])[:6], start=1):
                    st.markdown(f"**{idx}. {provider.get('resource_name', 'Provider')}**")
                    st.caption(
                        f"{provider.get('public_service_category', classify_provider_category(provider))} | "
                        f"{provider.get('confidence_label', 'Medium confidence')} | "
                        f"{provider.get('status', 'Needs human confirmation')}"
                    )
                    st.markdown(f"- Location: {provider.get('area_served') or provider.get('city') or 'Location not returned'}")
                    st.markdown(f"- Website status: {provider.get('website_status', 'See basic website check if available')}")
                    st.markdown(f"- Confidence note: {provider.get('confidence_reason', 'Needs human confirmation.')}")
                    st.markdown(f"- Next best action: {provider.get('next_best_action', 'Confirm hours, eligibility, and intake process.')}")
                    if provider.get("map_link"):
                        st.markdown(f"- [Map link]({provider.get('map_link')})")
                    contact = provider.get("group_email") or provider.get("phone") or "Contact not returned"
                    st.markdown(f"- Contact: {contact}")
                    st.divider()

        with st.container(border=True):
            st.subheader("Selected Provider Checks")
            if st.session_state.get("provider_checks"):
                checks_df = pd.DataFrame(st.session_state["provider_checks"])
                display_check_cols = [
                    col
                    for col in [
                        "provider_name",
                        "website_status",
                        "http_status",
                        "confidence",
                        "basic_contact_found",
                        "hours_label",
                        "cost_label",
                        "appointment_required",
                        "checked_at",
                    ]
                    if col in checks_df.columns
                ]
                st.dataframe(checks_df[display_check_cols], width="stretch")
                with st.expander("Provider website check details", expanded=False):
                    st.json(st.session_state["provider_checks"])
            else:
                st.info("No selected provider checks were run for this plan.")

        with st.container(border=True):
            st.subheader("Executive Map Summary")
            map_summary = st.session_state.get("map_summary", {})
            if map_summary:
                metric_cols = st.columns(4)
                metric_cols[0].metric("Providers", map_summary.get("total_providers", 0))
                metric_cols[1].metric("Reachable Websites", map_summary.get("reachable_websites", 0))
                metric_cols[2].metric("Need Confirmation", map_summary.get("needs_human_confirmation", 0))
                metric_cols[3].metric("Closest", map_summary.get("closest_provider", "Unknown"))
                st.write(map_summary.get("summary_text", "Map summary is unavailable."))
                st.markdown("**Coverage concerns**")
                for concern in map_summary.get("coverage_concerns", []):
                    st.markdown(f"- {concern}")
                st.markdown(f"**Suggested next map-based action:** {map_summary.get('suggested_next_action', '')}")
            else:
                st.info("Map summary is unavailable for this run.")

        with st.container(border=True):
            st.subheader("Map View")
            map_rows = st.session_state.get("map_rows", [])
            if map_rows:
                st.caption("Legend: Food, Shelter, Legal, Medical, Transportation, Utility Help, and Other are public-service categories inferred from public data.")
                st.map(pd.DataFrame(map_rows).rename(columns={"lon": "longitude", "lat": "latitude"}))
                for row in map_rows:
                    st.markdown(f"- [{row['resource_name']}]({row['map_link']})")
            else:
                st.info("No mapped provider results are available for this run.")
            if st.session_state.get("geocode_trace", {}).get("errors"):
                with st.expander("Location notes", expanded=False):
                    st.write(st.session_state["geocode_trace"]["errors"])

        with st.container(border=True):
            st.subheader("Gap Analysis")
            gap_items = (
                tool_result.get("access_barriers", [])
                + tool_result.get("eligibility_barriers", [])
                + tool_result.get("twenty_four_seven_gaps", [])
                + tool_result.get("validation_flags", [])
            )
            for item in gap_items or ["No major gap found in the available data. Confirm details directly before relying on any provider."]:
                st.markdown(f"- {item}")

        with st.container(border=True):
            st.subheader("Backup Options")
            for plan in tool_result.get("contingency_plans", []):
                st.markdown(f"**{plan['plan']}: {plan['title']}**")
                for step in plan["steps"]:
                    st.markdown(f"- {step}")

        with st.container(border=True):
            st.subheader("Outreach Email Drafts")
            draft = tool_result.get("smtp_email_draft", {})
            email_to = st.text_input("Recipient email", value=draft.get("recipient", ""), key="smtp_to")
            email_subject = st.text_input("Subject", value=draft.get("subject", ""), key="smtp_subject")
            email_body = st.text_area("Editable email body", value=draft.get("body", ""), height=220, key="smtp_body")
            if act_smtp:
                approved = st.checkbox("I reviewed and approve this email to be sent.", key="smtp_approved")
                if st.button("Send approved email", type="primary", width="stretch", key="send_approved_email"):
                    if not approved:
                        st.error("Review and approval are required before sending.")
                    else:
                        result = send_email_smtp(email_to, email_subject, email_body)
                        status = result.get("status", "failed")
                        log_agent_action(
                            st.session_state["agent_activity_log"],
                            "SMTP email sending",
                            status,
                            "real external API/tool data" if status == "completed" else "local/session data",
                            result.get("message", ""),
                            human_approval_required=True,
                        )
                        if result.get("sent"):
                            st.success(result["message"])
                        else:
                            st.warning(result["message"])
            else:
                st.caption("SMTP sending is off by default. Select Send approved email by SMTP before generating a plan to enable the send review controls.")

        with st.container(border=True):
            st.subheader("Call Script")
            st.caption("LIFT does not place phone calls. This script is prepared for the user to review and use when calling.")
            call_script = tool_result.get("call_script") or generate_call_script(
                st.session_state.get("user_need", ""),
                tool_result.get("matched_resources", [{}])[0] if tool_result.get("matched_resources") else {},
                language_access_needed,
            )
            st.text_area("Manual call script", value=call_script, height=210)

        with st.container(border=True):
            st.subheader("Tracker Rows")
            tracker_df = pd.DataFrame(tool_result.get("tracker_rows", []))
            if tracker_df.empty:
                st.info("No tracker rows were created for this run.")
            else:
                st.dataframe(tracker_df, width="stretch")

        with st.container(border=True):
            st.subheader("Downloads")
            if not tracker_df.empty:
                st.download_button(
                    "Download Tracker CSV",
                    data=tool_result.get("tracker_csv") or export_tracker_csv(tool_result.get("tracker_rows", [])),
                    file_name=f"lift_tracker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    width="stretch",
                )
            st.download_button(
                "Download Agent Activity Log CSV",
                data=log_df.to_csv(index=False),
                file_name=f"lift_agent_activity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                width="stretch",
            )

        with st.container(border=True):
            st.subheader("Agent Decision Trace")
            trace_tabs = st.tabs(["Route", "Tool", "Data", "Search Area Geocoding"])
            with trace_tabs[0]:
                st.json(st.session_state.get("route_trace", {}))
            with trace_tabs[1]:
                st.json(st.session_state.get("tool_trace", {}))
            with trace_tabs[2]:
                st.json(st.session_state.get("data_source_trace", {}))
            with trace_tabs[3]:
                st.json(st.session_state.get("search_area_geocode_trace", {}))

    return

    all_consents_checked = render_privacy_consent_section()
    st.divider()

    if not all_consents_checked:
        st.info("Check all required consent boxes above to enable the Generate button.")

    ui.render_soft_intro_card()

    st.header("1. Tell LIFT what you need")
    st.caption("A few words are enough to start. Example: find me a food pantry.")
    st.caption(f"Display language: {language} | Service language need: {language_access_needed}")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        user_need = st.text_area(
            "What does the user need help with?",
            placeholder=(
                "Example: I need a food pantry near Grand Rapids, but I work third shift "
                "and have limited transportation."
            ),
            height=140,
        )
        # Persist the user need in session state for use by other components
        st.session_state["user_need"] = user_need

    with col_right:
        resource_category = st.selectbox(
            get_text("Resource category", language),
            [
                "Any / Not Sure",
                "Food / Basic Needs",
                "Housing / Utilities",
                "Financial Assistance",
                "Transportation",
                "Legal / Administrative",
                "Behavioral Health",
                "Emergency / 24-7 Crisis",
                "Veteran / Service Member Support",
                "Family Readiness / FRG",
                "General Support / 24-7 Navigation",
            ],
        )

        urgency = st.selectbox(get_text("Urgency", language), ["Routine", "Soon", "Urgent", "Crisis / immediate"])

    st.header("2. Identify location and access limits")

    loc_col1, loc_col2, loc_col3 = st.columns(3)

    with loc_col1:
        primary_location = st.text_input(get_text("Primary search location", language), value="Grand Rapids, MI")

    with loc_col2:
        additional_locations_text = st.text_input(
            get_text("Additional locations", language),
            placeholder="Walker, MI; Kentwood, MI; Wyoming, MI",
        )

    with loc_col3:
        radius_miles = st.slider(get_text("Search radius in miles", language), 5, 100, 25, step=5)

    additional_locations = [
        item.strip()
        for item in additional_locations_text.replace(",", ";").split(";")
        if item.strip()
    ]

    st.header("3. Fit and eligibility context")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        audience = st.selectbox(
            "User type",
            [
                "Active-duty service member",
                "National Guard member",
                "Reservist",
                "Veteran",
                "Military spouse or partner",
                "Military-connected family",
                "Surviving spouse or family member",
                "Caregiver",
                "Dependent",
                "Parent or guardian",
                "Student",
                "Senior",
                "Person with a disability",
                "Unhoused or housing unstable",
                "Justice-impacted / reentry",
                "Community member",
                "Not sure",
                "Other",
            ],
        )

    with c2:
        transportation = st.selectbox("Transportation", ["Yes", "No", "Limited", "Public transit only"])

    with c3:
        needs_24_7 = st.selectbox("Needs 24/7 or after-hours option?", ["No", "Yes", "Not sure"])

    with c4:
        documents_available = st.selectbox("Documents available?", ["Yes", "No", "Not sure"])

    context = {
        "audience": audience,
        "transportation": transportation,
        "needs_24_7": needs_24_7,
        "documents_available": documents_available,
        "urgency": urgency,
        "display_language": language,
        "language_access_needed": language_access_needed,
    }

    # Optional Context (select only what you're comfortable sharing)
    with st.expander(get_text("Optional Context", language), expanded=False):
        st.caption(get_text("Select only what you are comfortable sharing. This helps match better resources.", language))
        optional_labels = [
            "Veteran",
            "Disabled Veteran",
            "Military family",
            "Single parent",
            "Parent/caregiver",
            "Pregnant/postpartum",
            "Student",
            "Senior",
            "Youth/young adult",
            "Housing unstable",
            "No transportation",
            "Low/no income",
            "Uninsured",
            "Food insecure",
            "Domestic Violence survivor",
            "Sexual assault survivor",
            "Mental health support",
            "Recovery support",
            "Legal help",
            "Reentry support",
            "Immigration help",
            "Spanish services",
            "LGBTQIA+ affirming",
            "Disability resources",
            "Pet-friendly help",
            "After-hours services",
        ]

        selected_optional = []
        cols = st.columns(3)
        for i, label in enumerate(optional_labels):
            col = cols[i % 3]
            if col.checkbox(label, key=f"optctx_{i}"):
                selected_optional.append(label)

    st.session_state["optional_context"] = selected_optional
    context["optional_context"] = selected_optional
    retrieval_trace = retrieve_curated_context(
        user_need=user_need,
        resource_category=resource_category,
        context=context,
    )
    context["retrieval_trace"] = retrieval_trace

    st.header("4. Follow-up outputs")

    selected_outputs = st.multiselect(
        "What should LIFT generate?",
        [
            "Resource fit summary",
            "Gap analysis",
            "Three contingency plans",
            "User-approved outreach draft",
            "Tracker rows",
            "System gap notes",
            "Map view",
            "CSV tracker download",
        ],
        default=[
            "Resource fit summary",
            "Gap analysis",
            "Three contingency plans",
            "User-approved outreach draft",
            "Tracker rows",
            "System gap notes",
            "Map view",
            "CSV tracker download",
        ],
    )

    api_key = get_openai_api_key()

    if not api_key:
        st.warning(
            "OPENAI_API_KEY is missing. Demo Mode will still call the external public data source when available, then run a clearly labeled fallback route. "
            "Demo Mode is interactive, but it is not a live LLM decision."
        )

    generate = st.button(
        get_text("Generate LIFT Plan", language),
        type="primary",
        width="stretch",
        disabled=not all_consents_checked,
    )

    if generate:
        if not user_need.strip():
            st.error("Enter a resource need first.")
            st.stop()

        input_errors, input_warnings = validate_user_input(user_need)
        for warning in input_warnings:
            st.warning(warning)
        if input_errors:
            for input_error in input_errors:
                st.error(input_error)
            st.stop()

        interpreted_intent = infer_intent_fallback(
            user_need=user_need,
            resource_category=resource_category,
            primary_location=primary_location,
            context=context,
        )

        if api_key and OPENAI_AVAILABLE:
            try:
                intent_client = get_openai_client()
                interpreted_intent = llm_interpret_request(
                    client=intent_client,
                    user_need=user_need,
                    resource_category=resource_category,
                    primary_location=primary_location,
                    additional_locations=additional_locations,
                    radius_miles=radius_miles,
                    context=context,
                )
            except Exception as error:
                interpreted_intent["interpretation_warning"] = (
                    f"Live LLM interpretation failed; fallback interpretation used: {type(error).__name__}"
                )

        context["interpreted_intent"] = interpreted_intent

        effective_resource_category = resource_category
        if resource_category == "Any / Not Sure" and interpreted_intent.get("need_type") in [
            "Food / Basic Needs",
            "Housing / Utilities",
            "Financial Assistance",
            "Transportation",
            "Legal / Administrative",
            "Behavioral Health",
            "Emergency / 24-7 Crisis",
            "Veteran / Service Member Support",
            "Family Readiness / FRG",
            "General Support / 24-7 Navigation",
        ]:
            effective_resource_category = interpreted_intent["need_type"]

        resources_df, data_source_trace = fetch_external_resource_data(
            user_need=user_need,
            resource_category=effective_resource_category,
            primary_location=primary_location,
            additional_locations=additional_locations,
            radius_miles=radius_miles,
        )
        resource_data = resources_df.to_dict(orient="records")

        with st.spinner("Running LIFT workflow..."):
            try:
                if api_key and OPENAI_AVAILABLE:
                    final_text, route_trace, tool_trace, tool_result = run_live_llm_tool_workflow(
                        user_need=user_need,
                        resource_category=effective_resource_category,
                        primary_location=primary_location,
                        additional_locations=additional_locations,
                        radius_miles=radius_miles,
                        context=context,
                        selected_outputs=selected_outputs,
                        resource_data=resource_data,
                        data_source_trace=data_source_trace,
                    )
                else:
                    route_trace = demo_route_decision(
                        user_need=user_need,
                        resource_category=effective_resource_category,
                        context=context,
                    )

                    tool_result = analyze_resource_gaps_and_build_contingency_plan(
                        user_need=user_need,
                        resource_category=effective_resource_category,
                        primary_location=primary_location,
                        additional_locations=additional_locations,
                        radius_miles=radius_miles,
                        context=context,
                        selected_outputs=selected_outputs,
                        resource_data=resource_data,
                    )

                    tool_trace = {
                        "tool_requested_by_model": False,
                        "tool_name": "analyze_resource_gaps_and_build_contingency_plan",
                        "tool_mode": "Demo fallback direct local call",
                        "external_data_source": data_source_trace,
                        "note": "This proves the workflow and custom tool output, but not live LLM tool-calling.",
                    }

                    final_text = build_demo_report(tool_result, route_trace)

                st.session_state["route_trace"] = route_trace
                st.session_state["tool_trace"] = tool_trace
                st.session_state["tool_result"] = tool_result
                st.session_state["data_source_trace"] = data_source_trace
                st.session_state["retrieval_trace"] = retrieval_trace
                st.session_state["interpreted_intent"] = interpreted_intent
                st.session_state["provider_checks"] = []
                st.session_state["current_case_record"] = {}
                st.session_state["final_text"] = final_text
                st.session_state["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            except Exception as error:
                st.error("The LIFT workflow could not run.")
                st.exception(error)

    if st.session_state.get("final_text"):
        st.divider()
        st.header("LIFT Output")
        translation_safety_note()

        interpreted_intent = st.session_state.get("interpreted_intent", {})
        if interpreted_intent:
            st.subheader("What LIFT understood")
            intent_cols = st.columns(4)
            with intent_cols[0]:
                st.metric("Need", interpreted_intent.get("need_type", "Unknown"))
            with intent_cols[1]:
                st.metric("Search Area", interpreted_intent.get("search_area", "Unknown"))
            with intent_cols[2]:
                st.metric("Urgency", str(interpreted_intent.get("urgency", "Unknown")).title())
            with intent_cols[3]:
                mode_label = "Live LLM" if "LIVE" in interpreted_intent.get("interpretation_mode", "") else "Demo"
                st.metric("Interpretation", mode_label)

            st.caption(interpreted_intent.get("plain_language_summary", ""))
            if interpreted_intent.get("barriers_or_preferences"):
                st.markdown(
                    "**Barriers/preferences noticed:** "
                    + "; ".join([str(item) for item in interpreted_intent.get("barriers_or_preferences", [])])
                )
            if interpreted_intent.get("missing_information"):
                st.markdown(
                    "**Helpful details still missing:** "
                    + "; ".join([str(item) for item in interpreted_intent.get("missing_information", [])])
                )
            if interpreted_intent.get("interpretation_warning"):
                st.warning(interpreted_intent["interpretation_warning"])
        
        # Agent Decision Trace
        st.subheader(f"🤖 {get_text('Agent Decision Trace', language)}")
        
        route_trace = st.session_state.get("route_trace", {})
        
        trace_col1, trace_col2, trace_col3 = st.columns(3)
        with trace_col1:
            st.metric("Selected Route", route_trace.get("selected_route", "unknown").replace("_", " ").title())
        with trace_col2:
            st.metric("Confidence", route_trace.get("confidence", "unknown").upper())
        with trace_col3:
            st.metric("Mode", "Live LLM" if "LIVE" in route_trace.get("routing_mode", "") else "Demo")
        
        st.markdown(f"**Reason:** {route_trace.get('reason', 'No reason provided')}")

        data_source_trace = st.session_state.get("data_source_trace", {})
        if data_source_trace:
            source_label = data_source_trace.get("data_source", "Unknown source")
            result_count = data_source_trace.get("result_count", 0)
            fallback_label = "fallback used" if data_source_trace.get("fallback_used") else "external API results"
            st.caption(f"Grounding source: {source_label} | {result_count} records | {fallback_label}")
        
        if route_trace.get("evidence"):
            st.markdown("**Evidence:**")
            for item in route_trace.get("evidence", []):
                st.markdown(f"- {item}")
        
        with st.expander("📋 Full Trace Details", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("AI Routing Decision")
                st.json(route_trace)
            with col2:
                st.subheader("Custom Tool Execution")
                st.json(st.session_state.get("tool_trace", {}))
            st.subheader("Structured Intent")
            st.json(interpreted_intent)
            st.subheader("External Data Call")
            st.json(data_source_trace)
            st.subheader("Curated Corpus Retrieval")
            st.json(st.session_state.get("retrieval_trace", {}))

        st.markdown(st.session_state["final_text"])

        tool_result = st.session_state["tool_result"]

        ui.render_result_cards_from_tool_result(tool_result)

        st.subheader("2. Review suggested resources")
        matched_df = pd.DataFrame(tool_result.get("matched_resources", []))

        if not matched_df.empty:
            visible_columns = [
                "resource_name",
                "category",
                "city",
                "area_served",
                "available_24_7",
                "business_hours",
                "phone",
                "group_email",
                "website",
                "eligibility",
                "status",
                "distance_miles",
            ]
            existing_columns = [col for col in visible_columns if col in matched_df.columns]
            provider_checks_by_name = {
                check.get("provider_name"): check
                for check in st.session_state.get("provider_checks", [])
            }
            selected_providers = []
            for idx, row in matched_df.iterrows():
                provider = provider_row_to_selection(row)
                with st.container(border=True):
                    top_cols = st.columns([0.08, 0.62, 0.3])
                    with top_cols[0]:
                        pursue = st.checkbox(
                            "Select",
                            value=(idx < min(2, len(matched_df))),
                            key=f"provider_select_{idx}",
                            label_visibility="collapsed",
                        )
                    with top_cols[1]:
                        st.markdown(f"**{provider['name']}**")
                        st.caption(f"{provider['category']} | {provider['city']} | {provider['status']}")
                    with top_cols[2]:
                        distance = provider.get("distance_miles")
                        distance_label = f"{distance} miles" if distance not in ["", None] else "Distance unknown"
                        st.caption(distance_label)
                        st.caption(f"Hours: {provider['business_hours']}")

                    detail_cols = st.columns(3)
                    with detail_cols[0]:
                        st.write(f"**Phone:** {provider['phone']}")
                    with detail_cols[1]:
                        st.write(f"**Email:** {provider['email']}")
                    with detail_cols[2]:
                        st.write(f"**Website:** {provider['website']}")

                    with st.expander("Why LIFT suggested this / what to verify", expanded=False):
                        st.write(f"Eligibility: {provider['eligibility']}")
                        st.write("Recommended verification: confirm current service, hours, intake steps, documents, and transportation requirements.")
                        check = provider_checks_by_name.get(provider["name"])
                        if check:
                            st.markdown("**Provider status check result**")
                            st.json(check)
                        else:
                            st.caption("No website/status check has been run for this provider yet.")

                    if pursue:
                        selected_providers.append(provider)

            with st.expander("Detailed resource table", expanded=False):
                st.dataframe(matched_df[existing_columns], width="stretch")

        
        st.subheader("3. Track follow-up actions")
        tracker_df = pd.DataFrame(tool_result.get("tracker_rows", []))

        if not tracker_df.empty:
            st.dataframe(tracker_df, width="stretch")
            csv_data = tracker_df.to_csv(index=False)
            st.download_button(
                "📥 Download Tracker CSV",
                data=csv_data,
                file_name=f"lift_tracker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                width="stretch",
            )

        # Ensure selected_providers exists
        try:
            selected_providers
        except NameError:
            selected_providers = []

        suggested_resources = []
        if not matched_df.empty:
            suggested_resources = [
                provider_row_to_selection(row)
                for _, row in matched_df.iterrows()
            ]

        existing_case_record = st.session_state.get("current_case_record", {})
        st.session_state["current_case_record"] = build_case_record(
            user_request=st.session_state.get("user_need", ""),
            interpreted_intent=st.session_state.get("interpreted_intent", {}),
            search_location=data_source_trace.get("queries", [""])[0] if data_source_trace else "",
            suggested_resources=suggested_resources,
            selected_resources=selected_providers,
            provider_checks=st.session_state.get("provider_checks", []),
            case_id=existing_case_record.get("case_id"),
            created_at=existing_case_record.get("created_at"),
        )

        # Basic provider checks for selected providers
        if selected_providers:
            st.subheader(f"4. {get_text('Basic Provider Check', language)}")
            st.caption(
                "This is a basic public HTTP provider check when a website URL is available. It is not full real-world verification. "
                "Confirm details directly with the provider before relying on them. Nothing is contacted automatically."
            )

            if not st.session_state.get("privacy_allow_website_checks", True):
                st.info("Provider website checks are disabled in Privacy Settings.")
            else:
                existing_provider_checks = st.session_state.get("provider_checks", [])
                if existing_provider_checks:
                    with st.expander("Previous selected provider checks", expanded=False):
                        st.json(existing_provider_checks)

                run_provider_checks = st.button(
                    "Run selected provider checks",
                    key="run_selected_provider_checks",
                    type="secondary",
                    width="stretch",
                )

                if run_provider_checks:
                    provider_checks = []

                    with st.spinner("Checking selected provider websites..."):
                        for c_idx, provider in enumerate(selected_providers):
                            check = mcp_basic_provider_check(
                                provider_name=provider.get("name", ""),
                                website_url=provider.get("website", ""),
                                category=provider.get("category", ""),
                                location=provider.get("city", ""),
                                user_need=st.session_state.get("user_need", ""),
                            )
                            provider_checks.append(check)

                    st.session_state["provider_checks"] = provider_checks
                    existing_case_record = st.session_state.get("current_case_record", {})
                    st.session_state["current_case_record"] = build_case_record(
                        user_request=st.session_state.get("user_need", ""),
                        interpreted_intent=st.session_state.get("interpreted_intent", {}),
                        search_location=data_source_trace.get("queries", [""])[0] if data_source_trace else "",
                        suggested_resources=suggested_resources,
                        selected_resources=selected_providers,
                        provider_checks=provider_checks,
                        case_id=existing_case_record.get("case_id"),
                        created_at=existing_case_record.get("created_at"),
                    )

                    for c_idx, check in enumerate(provider_checks):
                        provider_name = check.get("provider_name", f"Provider {c_idx + 1}")
                        with st.expander(f"{provider_name} - basic check", expanded=False):
                            st.write(f"**Website status:** {check.get('website_status', 'unknown')}")
                            st.write(f"**HTTP status:** {check.get('http_status', 'not available')}")
                            st.write(f"**Confidence:** {check.get('confidence', 'unknown')}")
                            st.write(f"**Basic contact found:** {check.get('basic_contact_found', 'unknown')}")
                            st.write(f"**Hours:** {check.get('hours_label', get_text('Hours unknown', language))}")
                            st.write(f"**Cost:** {check.get('cost_label', get_text('Cost unknown', language))}")
                            st.write(f"**Application required:** {check.get('application_required', 'unknown')}")
                            st.write(f"**Appointment required:** {check.get('appointment_required', 'unknown')}")
                            st.write(f"**Documents needed:** {check.get('documents_needed', 'unknown')}")
                            st.write(f"**Checked at:** {check.get('checked_at', 'unknown')}")
                            st.write(f"**Notes:** {check.get('notes', '')}")

                    with st.expander("Agent Decision Trace - selected provider checks", expanded=False):
                        st.json(provider_checks)

        # Generate warm outreach for selected providers
        if selected_providers:
            st.subheader("5. Generate follow-up and outreach")
            st.caption("**IMPORTANT:** These are drafts only. Nothing is sent automatically. Each draft requires human review and approval before use.")

            outreach_all = "LIFT AGENT - WARM OUTREACH DRAFTS\n"
            outreach_all += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            outreach_all += "IMPORTANT: These are drafts only. Nothing is sent automatically.\n"
            outreach_all += "Each draft requires human review and approval before use.\n\n"

            for p_idx, provider in enumerate(selected_providers):
                with st.expander(f"📬 {p_idx + 1}. {provider['name']}", expanded=(p_idx == 0)):
                    st.markdown(f"**Category:** {provider['category']}")
                    st.markdown(f"**Phone:** {provider['phone']} | **Email:** {provider['email']}")
                    st.markdown(f"**Hours:** {provider['business_hours']}")

                    # Subject line
                    subject = st.text_input(
                        "Email subject line",
                        value=f"Resource Fit / Eligibility Confirmation - {provider['category']}",
                        key=f"subj_{p_idx}"
                    )

                    # Email draft
                    email_text = st.text_area(
                        "Email draft",
                        value=(
                            "Hello,\n\n"
                            "I am reaching out to confirm whether your program may be a fit for someone seeking support related to a resource need.\n\n"
                            "I would appreciate confirmation on:\n"
                            "1. Whether your program currently provides this type of support\n"
                            "2. Eligibility requirements (location, age, income, military/veteran status, documents, etc.)\n"
                            "3. Current hours and whether after-hours or remote options exist\n"
                            "4. Best intake method (phone, email, website, walk-in, appointment, or referral)\n"
                            "5. Whether transportation or in-person attendance is required\n"
                            f"6. Whether {language_access_needed} language support or interpreter support is available\n\n"
                            "I am not asking for a referral at this time. I am only trying to verify fit, availability, and next steps.\n\n"
                            "Thank you for your time."
                        ),
                        height=200,
                        key=f"email_{p_idx}"
                    )

                    # Call script
                    call_script = st.text_area(
                        "Call script",
                        value=(
                            f"Hi, is this {provider['name']}? I'm calling to quickly verify a few things:\n\n"
                            "1. Do you provide [TYPE OF SUPPORT]?\n"
                            "2. What are the key eligibility requirements?\n"
                            "3. What are your hours? Do you have after-hours options?\n"
                            "4. Is it first-come or do we need to call ahead/make an appointment?\n"
                            "5. What's the best way to get someone started?\n"
                            f"6. Do you have {language_access_needed} language support or interpreter access?\n\n"
                            "Thank you - I'll get back to them with this information."
                        ),
                        height=150,
                        key=f"call_{p_idx}"
                    )

                    # Confirm before contacting
                    st.markdown("**Confirm before reaching out to this provider:**")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.checkbox("Eligibility requirements understood", key=f"conf_elig_{p_idx}")
                        st.checkbox("Hours confirmed", key=f"conf_hours_{p_idx}")
                    with col_b:
                        st.checkbox("Intake process known", key=f"conf_intake_{p_idx}")
                        st.checkbox("Contact method selected", key=f"conf_contact_{p_idx}")

                    follow_date = st.date_input("Follow-up date", key=f"fup_{p_idx}")

                    # Build export content
                    outreach_all += f"\n{'='*70}\n"
                    outreach_all += f"PROVIDER {p_idx + 1}: {provider['name']}\n"
                    outreach_all += f"{'='*70}\n"
                    outreach_all += f"Category: {provider['category']}\n"
                    outreach_all += f"Phone: {provider['phone']}\n"
                    outreach_all += f"Email: {provider['email']}\n"
                    outreach_all += f"Website: {provider['website']}\n"
                    outreach_all += f"Hours: {provider['business_hours']}\n"
                    outreach_all += f"Eligibility: {provider['eligibility']}\n"
                    outreach_all += f"Follow-up date: {follow_date}\n\n"
                    outreach_all += f"SUBJECT: {subject}\n\n"
                    outreach_all += "--- EMAIL DRAFT ---\n"
                    outreach_all += email_text + "\n\n"
                    outreach_all += "--- CALL SCRIPT ---\n"
                    outreach_all += call_script + "\n"

            # Download all outreach
            st.download_button(
                "📄 Download All Outreach Drafts",
                data=outreach_all,
                file_name=f"lift_outreach_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                width="stretch"
            )
        else:
            st.info("💡 Select providers above to generate warm outreach drafts.")

        case_record = st.session_state.get("current_case_record", {})
        if case_record:
            st.subheader("6. Save/export this session case")
            st.info(
                "Session-only MVP: LIFT keeps this case summary in browser session state. "
                "It is not permanently stored unless you download/export it."
            )

            summary_cols = st.columns(4)
            with summary_cols[0]:
                st.metric("Case ID", case_record.get("case_id", ""))
            with summary_cols[1]:
                st.metric("Suggested", case_record.get("suggested_resource_count", 0))
            with summary_cols[2]:
                st.metric("Selected", len(case_record.get("selected_resources", [])))
            with summary_cols[3]:
                st.metric("Follow-ups", len(case_record.get("followup_actions", [])))

            with st.expander("Case summary details", expanded=False):
                st.json(case_record)

            case_summary_text = format_case_summary(case_record)
            st.download_button(
                "Download Case Summary",
                data=case_summary_text,
                file_name=f"{case_record.get('case_id', 'lift_case')}.txt",
                mime="text/plain",
                width="stretch",
            )

            if st.button("Save case to this session", width="stretch"):
                st.session_state["case_history"].append(case_record)
                st.success("Saved to this session's case history.")

            if st.session_state.get("case_history"):
                with st.expander("Session case history", expanded=False):
                    st.json(st.session_state["case_history"])


def render_about_page():
    st.header("About LIFT Agent")

    st.markdown(
        """
**LIFT Agent** stands for **Locate. Identify. Follow-up. Track.**

LIFT Agent is a human-supervised autonomous resource navigation agent. It can search public provider information, check public provider websites, generate mapped results, create outreach drafts, send approved emails through SMTP, and build follow-up tracker rows.

Phone calls remain manual. LIFT does not place phone calls, monitor voicemail, scan inboxes, or claim that it reached a provider by phone. It prepares the call plan, script, checklist, and tracker row for the user.

### What LIFT Does

- Uses public external search data when available
- Supports multiple locations and radius-based matching
- Checks public provider websites when selected
- Uses Google Maps/geocoding when configured
- Flags transportation, documentation, eligibility, and validation barriers
- Generates user-approved outreach drafts
- Sends approved SMTP email only after explicit review and approval
- Generates tracker rows, CSV downloads, and agent activity logs
"""
    )

    st.subheader("Project 3 Agentic Workflow")

    workflow_steps = [
        ("1", "User Need", "The user enters a resource need, location, and context."),
        ("2", "LLM Route Decision", "The model selects the next workflow route when the API key is available."),
        ("3", "External Data + Custom Tool Call", "The app calls a public search API, then passes normalized records into the custom LIFT tool for resource fit and gap review."),
        ("4", "Resource Fit + Gap Analysis", "The tool reviews matches, barriers, eligibility, hours, and access issues."),
        ("5", "Outreach + Tracker", "The app drafts outreach and creates follow-up tracker rows."),
        ("6", "User Approval Layer", "The user reviews everything before using any outreach."),
    ]

    for number, title, description in workflow_steps:
        st.markdown(
            f"""
            <div style="border:1px solid #999; border-radius:10px; padding:14px; margin-bottom:10px;">
                <h4 style="margin:0;">{number}. {title}</h4>
                <p style="margin:6px 0 0 0; font-size:16px;">{description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_monitoring_page():
    st.header("Validation / Monitoring Notes")

    st.markdown(
        """
This section documents the future validation concept.

For the working draft, validation is manual and based on public search results. A production version could validate:

- Website availability
- Main office phone
- Group mailbox
- Business hours
- 24/7 availability
- Eligibility requirements
- Whether the resource still serves the listed area

The app should avoid relying on one individual point of contact because people rotate. Stable contacts are preferred:

- Main office phone
- Group mailbox
- Official program website
- Hotline
- Intake desk
"""
    )

    old_status = st.text_area("Previous resource note", height=120)
    new_status = st.text_area("Updated resource note", height=120)

    if st.button("Compare Notes"):
        if not old_status.strip() or not new_status.strip():
            st.error("Paste both notes first.")
        else:
            st.write("Manual comparison draft:")
            st.write(f"Previous length: {len(old_status)} characters")
            st.write(f"Updated length: {len(new_status)} characters")

            if old_status.strip() == new_status.strip():
                st.success("No change detected.")
            else:
                st.warning("Change detected. A future version could summarize this with the LLM.")


def main():
    st.set_page_config(page_title=APP_NAME, page_icon="✨", layout="wide")

    # Initialize session state
    init_session_state()

    # Visual redesign
    ui.inject_global_styles()

    # Main guided intake page
    ui.render_brand_header(app_name=APP_NAME, author_line="from Britney Katherine Lindsey")
    lang_cols = st.columns([1, 2])
    with lang_cols[0]:
        language_options = ["English", "Spanish", "Italian"]
        current_language = st.session_state.get("language", "English")
        st.session_state["language"] = st.selectbox(
            "Language",
            language_options,
            index=language_options.index(current_language) if current_language in language_options else 0,
            key="top_language_select_clean",
        )
    ui.render_scroll_cta(target_anchor_id="lift-form-section", label="Start your LIFT plan")
    st.markdown("A guided plan for finding resource options, checking barriers, preparing outreach, and tracking next steps.")
    st.markdown('<div class="lift-hero-art-wrap">', unsafe_allow_html=True)
    ui.render_hover_animation(width_px=220, height_px=220, frame_delay_ms=1300)
    st.markdown("</div>", unsafe_allow_html=True)
    ui.render_anchor("lift-form-section")
    render_generate_page()

    st.divider()
    with st.container(border=True):
        st.markdown("**Navigation**")
        footer_cols = st.columns(5)
        footer_cols[0].markdown("Language")
        footer_cols[1].markdown("About LIFT")
        footer_cols[2].markdown("How LIFT Works")
        footer_cols[3].markdown("Privacy")
        footer_cols[4].markdown("Evidence / Project Notes")

    with st.expander("How LIFT Works", expanded=False):
        st.markdown(
            """
**Locate:** find public resource options based on need, location, and access limits.

**Identify:** notice barriers early, like hours, eligibility, transportation, documents, or cost.

**Follow-up:** create respectful outreach language the user can review before using.

**Track:** create tracker rows, next actions, due dates, and notes so nothing gets lost.
"""
        )
        ui.render_hover_animation(width_px=300, height_px=300, frame_delay_ms=1200)

    with st.expander("Privacy and Consent", expanded=False):
        st.markdown(
            """
LIFT uses public resource data and provider website checks when available. Output history is session-only unless the user downloads it. Email sending requires SMTP configuration, a reviewed draft, an approved recipient, and explicit approval.

LIFT does not call providers, monitor voicemail, or scan inboxes. Phone calls remain a user action.
"""
        )

    with st.expander("About LIFT Agent", expanded=False):
        render_about_page()

    with st.expander("Project Evidence", expanded=False):
        st.markdown(
            """
Evidence files in this repository document the agent loop, tool functions, real-world integrations, fallback handling, and test notes.

- `Evidence/AGENT_WORKFLOW_EVIDENCE.md`
- `Evidence/TEST_RUN_NOTES.md`
"""
        )


if __name__ == "__main__":
    main()

