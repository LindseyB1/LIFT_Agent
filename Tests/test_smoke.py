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


if __name__ == "__main__":
    unittest.main()
