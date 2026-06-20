import json
import math
import os
import socket
import time
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd
import streamlit as st

import ui_components as ui

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

# Supported languages
SUPPORTED_LANGUAGES = [
    "English",
    "Spanish",
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
    st.divider()
    all_consents_checked = render_privacy_consent_section()
    st.divider()

    if not all_consents_checked:
        st.info("Check all required consent boxes above to enable the Generate button.")

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

    return "\n".join(lines)


def init_session_state():
    """Initialize required session state variables for consent and privacy."""
    if "consent_synthetic_data" not in st.session_state:
        st.session_state["consent_synthetic_data"] = False
    if "consent_no_sensitive_data" not in st.session_state:
        st.session_state["consent_no_sensitive_data"] = False
    if "consent_no_automation" not in st.session_state:
        st.session_state["consent_no_automation"] = False
    if "consent_human_approval" not in st.session_state:
        st.session_state["consent_human_approval"] = False
    if "privacy_session_only" not in st.session_state:
        st.session_state["privacy_session_only"] = False
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


def render_privacy_consent_section():
    """Render the Privacy, Consent, and User Control section."""
    st.header(t("Privacy, Consent, and User Control"))
    
    st.markdown(
        """
**LIFT Agent is a draft tool using public external search data when available, with clearly labeled demo fallback data if the external API is unavailable.** 
This app does not send emails, call providers, monitor voicemail, scan inboxes, or store case files without your explicit consent and approval at every step.
        """
    )
    
    st.subheader("Required Consent Checkboxes")
    st.markdown("**All of the following must be checked before you can generate a LIFT plan:**")
    
    col1, col2 = st.columns([0.05, 0.95])
    with col1:
        st.write("")
    with col2:
        st.session_state["consent_synthetic_data"] = st.checkbox(
            "☑ I understand this draft uses public external search data or clearly labeled demo fallback information only.",
            value=st.session_state.get("consent_synthetic_data", False),
            key="consent_synthetic_check"
        )
    
    col1, col2 = st.columns([0.05, 0.95])
    with col1:
        st.write("")
    with col2:
        st.session_state["consent_no_sensitive_data"] = st.checkbox(
            "☑ I will not enter private, classified, restricted, protected, or sensitive personal information.",
            value=st.session_state.get("consent_no_sensitive_data", False),
            key="consent_no_sensitive_check"
        )
    
    col1, col2 = st.columns([0.05, 0.95])
    with col1:
        st.write("")
    with col2:
        st.session_state["consent_no_automation"] = st.checkbox(
            "☑ I understand this app does not send emails, contact providers, scan inboxes, monitor phones, or access voicemail.",
            value=st.session_state.get("consent_no_automation", False),
            key="consent_no_automation_check"
        )
    
    col1, col2 = st.columns([0.05, 0.95])
    with col1:
        st.write("")
    with col2:
        st.session_state["consent_human_approval"] = st.checkbox(
            "☑ I understand AI-generated outreach must be reviewed and approved by a human before use.",
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
        "or sensitive information. This draft does not send emails, monitor phones, access voicemail, or scan inboxes."
    )


def render_generate_page():
    language = current_language()
    language_access_needed = st.session_state.get("language_access_needed", "No preference")

    ui.render_soft_intro_card()

    st.header("1. Locate the need")
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
                "Service member",
                "Veteran",
                "Military-connected family",
                "Caregiver",
                "Dependent",
                "Community member",
                "Not sure",
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
        use_container_width=True,
        disabled=not all_consents_checked,
    )

    if generate:
        if not user_need.strip():
            st.error("Enter a resource need first.")
            st.stop()

        resources_df, data_source_trace = fetch_external_resource_data(
            user_need=user_need,
            resource_category=resource_category,
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
                        resource_category=resource_category,
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
                        resource_category=resource_category,
                        context=context,
                    )

                    tool_result = analyze_resource_gaps_and_build_contingency_plan(
                        user_need=user_need,
                        resource_category=resource_category,
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
                st.session_state["final_text"] = final_text
                st.session_state["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            except Exception as error:
                st.error("The LIFT workflow could not run.")
                st.exception(error)

    if st.session_state.get("final_text"):
        st.divider()
        st.header("LIFT Output")
        translation_safety_note()
        
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
            st.subheader("External Data Call")
            st.json(data_source_trace)

        st.markdown(st.session_state["final_text"])

        tool_result = st.session_state["tool_result"]

        ui.render_result_cards_from_tool_result(tool_result)

        st.subheader("👥 Matched Resources - Select Providers to Pursue")
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
            st.dataframe(matched_df[existing_columns], use_container_width=True)
            
            # Provider selection
            st.subheader("Which providers do you want to pursue?")
            selected_providers = []
            for idx, row in matched_df.iterrows():
                if st.checkbox(
                    f"✓ {row['resource_name']} ({row['category']})",
                    value=(idx < min(2, len(matched_df))),  # Select first 2 by default
                    key=f"provider_select_{idx}"
                ):
                    selected_providers.append({
                        "name": row["resource_name"],
                        "category": row["category"],
                        "phone": row.get("phone", "N/A"),
                        "email": row.get("group_email", "N/A"),
                        "website": row.get("website", "N/A"),
                        "business_hours": row.get("business_hours", "N/A"),
                        "eligibility": row.get("eligibility", "N/A"),
                        "city": row.get("city", "N/A"),
                    })

        
        st.subheader("📋 Follow-Up Tracker")
        tracker_df = pd.DataFrame(tool_result.get("tracker_rows", []))

        if not tracker_df.empty:
            st.dataframe(tracker_df, use_container_width=True)
            csv_data = tracker_df.to_csv(index=False)
            st.download_button(
                "📥 Download Tracker CSV",
                data=csv_data,
                file_name=f"lift_tracker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        # Ensure selected_providers exists
        try:
            selected_providers
        except NameError:
            selected_providers = []

        # Basic provider checks for selected providers
        if selected_providers:
            st.subheader(f"🔎 {get_text('Basic Provider Check', language)}")
            st.caption(
                "This is a basic public HTTP provider check when a website URL is available. It is not full real-world verification. "
                "Confirm details directly with the provider before relying on them. Nothing is contacted automatically."
            )

            existing_provider_checks = st.session_state.get("provider_checks", [])
            if existing_provider_checks:
                with st.expander("Previous selected provider checks", expanded=False):
                    st.json(existing_provider_checks)

            run_provider_checks = st.button(
                "Run selected provider checks",
                key="run_selected_provider_checks",
                type="secondary",
                use_container_width=True,
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

                for c_idx, check in enumerate(provider_checks):
                    provider_name = check.get("provider_name", f"Provider {c_idx + 1}")
                    with st.expander(f"{provider_name} - basic check", expanded=False):
                        st.write(f"**Website status:** {check.get('website_status', 'unknown')}")
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
            st.subheader("✉️ Warm Outreach Drafts (Per Selected Provider)")
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
                use_container_width=True
            )
        else:
            st.info("💡 Select providers above to generate warm outreach drafts.")


def render_about_page():
    st.header("About LIFT Agent")

    st.markdown(
        """
**LIFT Agent** stands for **Locate. Identify. Follow-up. Track.**

This Project 3 draft is not a generic chatbot and not a static resource list. It is designed to show an agentic workflow:

1. The user enters a resource need.
2. The app collects location, radius, eligibility, and access context.
3. The LLM selects a route when an API key is available.
4. The model calls a custom tool.
5. The tool generates resource matches, barriers, contingency options, outreach drafts, tracker rows, and system gap notes.
6. The user remains the approval layer before any outreach is used.

### What this draft does

- Uses public external search data when available
- Supports multiple locations and radius-based matching
- Separates 24/7 support from business-hours resources
- Flags transportation, documentation, eligibility, and validation barriers
- Generates user-approved outreach drafts
- Generates tracker rows and CSV downloads
- Shows visible route and tool traces

### What this draft does not do

- It does not send emails
- It does not call providers
- It does not monitor voicemail
- It does not scan inboxes
- It does not store private case files
- It does not claim real-world verification

Future versions could add consent-based integrations, login, role-based access, audit logs, limited permissions, and data retention controls.
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

    # Visual redesign and optional advanced sidebar
    ui.inject_global_styles()
    ui.render_advanced_sidebar(
        supported_languages=SUPPORTED_LANGUAGES,
        openai_available=OPENAI_AVAILABLE,
        api_key_present=bool(get_openai_api_key()),
    )

    # Main, always-rendered, single scrolling page
    ui.render_brand_header(app_name=APP_NAME, author_line="from Britney Katherine Lindsey")
    ui.render_hover_animation()
    ui.render_scroll_cta(target_anchor_id="lift-explainer-section", label="Let’s LIFT You Up")

    ui.render_anchor("lift-explainer-section")
    ui.render_lift_explainer()

    ui.render_anchor("lift-form-section")
    render_generate_page()

    st.divider()
    with st.expander("About LIFT Agent", expanded=False):
        render_about_page()

    with st.expander("Validation / Monitoring Notes", expanded=False):
        render_monitoring_page()


if __name__ == "__main__":
    main()
