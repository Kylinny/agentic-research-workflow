import unittest

from tools.hybrid_retrieval import HybridRetrievalTool


class HybridRetrievalFallbackTest(unittest.TestCase):
    def test_keyword_only_search_works_without_semantic_backend(self):
        tool = HybridRetrievalTool(data_dir="data")

        results = tool.search("biotechnology", doc_type="x_posts", top_k=3)

        self.assertTrue(results)
        self.assertEqual(results[0]["retrieval_mode"], "keyword_only")
        self.assertIn("semantic_backend_error", results[0])


if __name__ == "__main__":
    unittest.main()
