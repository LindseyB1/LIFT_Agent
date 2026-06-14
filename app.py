import json
import math
import os
from datetime import datetime

import pandas as pd
import streamlit as st

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
APP_SUBTITLE = "AI-assisted resource matching, gap review, outreach drafting, and follow-up tracking."

DEFAULT_MODEL = os.getenv("P3_DEFAULT_MODEL", "gpt-4o-mini")


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
            "Analyze a user's resource need, location/radius, eligibility context, and synthetic resource data. "
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
        matches["matched_location"] = "Fallback synthetic match"

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
            "No major validation issue identified in the synthetic data, but real-world use would require phone/website verification."
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
        "This draft uses synthetic/public-style data only.",
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
                },
                indent=2,
            ),
        },
    ]

    first_response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        tools=[ANALYZE_RESOURCE_GAP_TOOL],
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
        if tool_call.function.name != "analyze_resource_gaps_and_build_contingency_plan":
            raise RuntimeError(f"Unexpected tool requested: {tool_call.function.name}")

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

    final_instruction = """
Write a concise structured report using the tool result.
Include:
1. Best-fit resource summary
2. Main access/eligibility gaps
3. Three contingency options
4. Outreach draft note
5. Tracker next steps
6. System gap note

Do not claim real-world verification. State that resource data is synthetic/public-style draft data.
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


def render_privacy_notice():
    st.info(
        "Use public or synthetic information only. Do not enter private, classified, restricted, protected, "
        "or sensitive information. This draft does not send emails, monitor phones, access voicemail, or scan inboxes."
    )


def render_generate_page():
    st.header("1. Locate the need")

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

    with col_right:
        resource_category = st.selectbox(
            "Resource category",
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

        urgency = st.selectbox("Urgency", ["Routine", "Soon", "Urgent", "Crisis / immediate"])

    st.header("2. Identify location and access limits")

    loc_col1, loc_col2, loc_col3 = st.columns(3)

    with loc_col1:
        primary_location = st.text_input("Primary search location", value="Grand Rapids, MI")

    with loc_col2:
        additional_locations_text = st.text_input(
            "Additional locations",
            placeholder="Walker, MI; Kentwood, MI; Wyoming, MI",
        )

    with loc_col3:
        radius_miles = st.slider("Search radius in miles", 5, 100, 25, step=5)

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
    }

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
            "OPENAI_API_KEY is missing. Demo Mode will run with synthetic data and a clearly labeled fallback route. "
            "Demo Mode is interactive, but it is not a live LLM decision."
        )

    generate = st.button("Generate LIFT Plan", type="primary", use_container_width=True)

    if generate:
        if not user_need.strip():
            st.error("Enter a resource need first.")
            st.stop()

        resources_df = synthetic_resource_data()
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
                        "note": "This proves the workflow and custom tool output, but not live LLM tool-calling.",
                    }

                    final_text = build_demo_report(tool_result, route_trace)

                st.session_state["route_trace"] = route_trace
                st.session_state["tool_trace"] = tool_trace
                st.session_state["tool_result"] = tool_result
                st.session_state["final_text"] = final_text
                st.session_state["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            except Exception as error:
                st.error("The LIFT workflow could not run.")
                st.exception(error)

    if st.session_state.get("final_text"):
        st.divider()
        st.header("LIFT Output")

        trace_col1, trace_col2 = st.columns(2)

        with trace_col1:
            st.subheader("AI Decision Trace")
            st.json(st.session_state["route_trace"])

        with trace_col2:
            st.subheader("Custom Tool Trace")
            st.json(st.session_state["tool_trace"])

        st.markdown(st.session_state["final_text"])

        tool_result = st.session_state["tool_result"]

        st.subheader("Matched Resources")
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

            if "Map view" in selected_outputs and {"lat", "lon"}.issubset(matched_df.columns):
                st.subheader("Map View")
                st.map(matched_df.rename(columns={"lat": "latitude", "lon": "longitude"}))

        st.subheader("Tracker Rows")
        tracker_df = pd.DataFrame(tool_result.get("tracker_rows", []))

        if not tracker_df.empty:
            st.dataframe(tracker_df, use_container_width=True)

            csv_data = tracker_df.to_csv(index=False)

            st.download_button(
                "Download Tracker CSV",
                data=csv_data,
                file_name=f"lift_tracker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        st.subheader("Outreach Draft Approval")
        st.caption("Draft only. The app does not send this message.")
        outreach_text = st.text_area(
            "Review/edit outreach draft",
            value=tool_result.get("outreach_email_draft", ""),
            height=260,
        )

        st.checkbox(
            "I reviewed this draft. I understand LIFT does not send outreach automatically.",
            value=False,
        )

        st.download_button(
            "Download Outreach Draft",
            data=outreach_text,
            file_name=f"lift_outreach_draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True,
        )


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

- Uses synthetic/public-style data
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

    st.graphviz_chart(
        """
        digraph {
            rankdir=LR;

            intake [label="User need + location + context"];
            router [label="LLM route decision"];
            tool [label="Custom tool call"];
            analysis [label="Resource fit + gap analysis"];
            outputs [label="Outreach draft + tracker + gap notes"];
            approval [label="User approval layer"];

            intake -> router;
            router -> tool;
            tool -> analysis;
            analysis -> outputs;
            outputs -> approval;
        }
        """
    )


def render_monitoring_page():
    st.header("Validation / Monitoring Notes")

    st.markdown(
        """
This section documents the future validation concept.

For the working draft, validation is manual and synthetic. A production version could validate:

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
    st.set_page_config(page_title=APP_NAME, page_icon="🧭", layout="wide")

    st.title(APP_NAME)
    st.caption(f"{APP_TAGLINE} | {APP_SUBTITLE}")

    render_privacy_notice()

    page = st.sidebar.radio("Navigation", ["Generate LIFT Plan", "Validation Notes", "About"])

    if page == "Generate LIFT Plan":
        render_generate_page()
    elif page == "Validation Notes":
        render_monitoring_page()
    else:
        render_about_page()


if __name__ == "__main__":
    main()
