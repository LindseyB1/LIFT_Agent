import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class LiftSmokeTests(unittest.TestCase):
    def test_imports_and_core_helpers_exist(self):
        import app
        import p3_tools
        import security_utils

        self.assertTrue(hasattr(app, "analyze_resource_gaps_and_build_contingency_plan"))
        self.assertTrue(hasattr(app, "retrieve_curated_context"))
        self.assertTrue(hasattr(app, "infer_intent_fallback"))
        self.assertTrue(hasattr(app, "build_case_record"))
        self.assertTrue(hasattr(app, "search_public_resources"))
        self.assertTrue(hasattr(app, "check_provider_website"))
        self.assertTrue(hasattr(app, "geocode_provider_locations"))
        self.assertTrue(hasattr(app, "render_google_map"))
        self.assertTrue(hasattr(app, "generate_outreach_email"))
        self.assertTrue(hasattr(app, "generate_call_script"))
        self.assertTrue(hasattr(app, "create_tracker_rows"))
        self.assertTrue(hasattr(app, "export_tracker_csv"))
        self.assertTrue(hasattr(app, "send_email_smtp"))
        self.assertTrue(hasattr(app, "write_agent_audit_log"))
        self.assertTrue(hasattr(p3_tools, "analyze_project_request"))
        self.assertTrue(hasattr(security_utils, "validate_user_input"))

    def test_curated_retrieval_returns_citations(self):
        import app

        trace = app.retrieve_curated_context(
            user_need="Food pantry after hours with limited transportation",
            resource_category="Food / Basic Needs",
            context={
                "transportation": "Limited",
                "needs_24_7": "Yes",
                "documents_available": "Not sure",
                "optional_context": ["Food insecure", "After-hours services"],
            },
        )

        self.assertEqual(trace["retrieval_mode"], "local_curated_corpus")
        self.assertGreaterEqual(len(trace["retrieved_chunks"]), 1)
        self.assertGreaterEqual(len(trace["inline_citations"]), 1)

    def test_demo_tool_result_is_structured_and_cited(self):
        import app

        resources = app.synthetic_resource_data().to_dict(orient="records")
        context = {
            "audience": "Community member",
            "transportation": "Limited",
            "needs_24_7": "Yes",
            "documents_available": "Not sure",
            "optional_context": ["Food insecure"],
        }
        context["retrieval_trace"] = app.retrieve_curated_context(
            "Need after-hours food pantry near Grand Rapids",
            "Food / Basic Needs",
            context,
        )

        result = app.analyze_resource_gaps_and_build_contingency_plan(
            user_need="Need after-hours food pantry near Grand Rapids",
            resource_category="Food / Basic Needs",
            primary_location="Grand Rapids, MI",
            additional_locations=["Wyoming, MI"],
            radius_miles=25,
            context=context,
            selected_outputs=[
                "Resource fit summary",
                "Gap analysis",
                "Three contingency plans",
                "Tracker rows",
            ],
            resource_data=resources,
        )

        self.assertGreaterEqual(len(result["matched_resources"]), 1)
        self.assertEqual(len(result["contingency_plans"]), 3)
        self.assertGreaterEqual(len(result["tracker_rows"]), 1)
        self.assertIn("retrieval_trace", result)
        self.assertGreaterEqual(len(result["citations"]), 1)

    def test_short_request_intent_and_case_record(self):
        import app

        context = {
            "transportation": "Limited",
            "needs_24_7": "Not sure",
            "documents_available": "Not sure",
            "urgency": "Routine",
            "optional_context": [],
        }
        intent = app.infer_intent_fallback(
            user_need="find me a food pantry",
            resource_category="Any / Not Sure",
            primary_location="Grand Rapids, MI",
            context=context,
        )
        self.assertEqual(intent["need_type"], "Food / Basic Needs")
        self.assertIn("DEMO FALLBACK", intent["interpretation_mode"])

        selected = [
            {
                "name": "Example Pantry",
                "category": "Food / Basic Needs",
                "phone": "616-555-0101",
                "email": "intake@example.org",
                "website": "https://example.org",
            }
        ]
        case_record = app.build_case_record(
            user_request="find me a food pantry",
            interpreted_intent=intent,
            search_location="Grand Rapids, MI",
            suggested_resources=selected,
            selected_resources=selected,
            provider_checks=[],
        )
        self.assertEqual(case_record["suggested_resource_count"], 1)
        self.assertEqual(len(case_record["followup_actions"]), 1)
        self.assertIn("Session only", case_record["storage_mode"])

    def test_provider_check_without_url_has_visible_status_shape(self):
        import app

        result = app.mcp_basic_provider_check(
            provider_name="No URL Provider",
            website_url="Not returned by API",
            category="Food / Basic Needs",
            location="Grand Rapids, MI",
        )
        self.assertEqual(result["website_status"], "unknown")
        self.assertIn("http_status", result)
        self.assertEqual(result["confidence"], "low")


if __name__ == "__main__":
    unittest.main()
