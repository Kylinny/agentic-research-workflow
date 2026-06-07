import unittest

from agent import ResearchAgent
from grok import OfflineGrokClient


class OfflineWorkflowTest(unittest.TestCase):
    def test_research_agent_completes_query_offline(self):
        agent = ResearchAgent(
            grok_client=OfflineGrokClient(),
            data_dir="data",
        )

        result = agent.research(
            "How does X discourse on biotechnology compare to academic research?",
            verbose=False,
        )

        self.assertTrue(result["success"])
        self.assertGreaterEqual(result["successful_tasks"], 1)
        self.assertEqual(result["iterations"], 1)


if __name__ == "__main__":
    unittest.main()
