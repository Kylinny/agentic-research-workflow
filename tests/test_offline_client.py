import json
import unittest

from grok import GrokModel, OfflineGrokClient


class OfflineGrokClientTest(unittest.TestCase):
    def setUp(self):
        self.client = OfflineGrokClient()

    def test_planner_returns_hybrid_retrieval_plan_for_x_query(self):
        response = self.client.chat_completion(
            messages=[
                {"role": "system", "content": "You are an expert research planning agent."},
                {"role": "user", "content": "Research Query: What are people saying on X about AI safety?\n\nCreate a detailed execution plan."},
            ],
            model=GrokModel.GROK_4_LATEST,
        )

        plan = json.loads(response["content"])

        self.assertEqual(plan["sub_tasks"][0]["tool"], "hybrid_retrieval")
        self.assertEqual(plan["sub_tasks"][0]["parameters"]["doc_type"], "x_posts")

    def test_analyzer_returns_completion_threshold_for_successful_results(self):
        response = self.client.chat_completion(
            messages=[
                {"role": "system", "content": "You are an expert at analyzing research results and determining next steps."},
                {"role": "user", "content": "Task 1 (paper_search):\n{\"title\": \"Example Paper\"}"},
            ],
            model=GrokModel.GROK_4_LATEST,
        )

        analysis = json.loads(response["content"])

        self.assertGreaterEqual(analysis["quality_score"], 8.0)
        self.assertGreaterEqual(analysis["completeness"], 8.0)
        self.assertFalse(analysis["needs_replanning"])


if __name__ == "__main__":
    unittest.main()
