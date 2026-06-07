import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evaluation.run_benchmark import run_benchmark
from grok import GrokModel


class OfflineBenchmarkTest(unittest.TestCase):
    def test_offline_benchmark_writes_results(self):
        queries = [
            {
                "id": 1,
                "query": "What are the main concerns about AI safety discussed on X?",
                "category": "x_analysis",
                "complexity": "medium",
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("evaluation.run_benchmark.time.sleep", return_value=None):
                output = run_benchmark(
                    queries,
                    model=GrokModel.GROK_4_LATEST,
                    output_dir=temp_dir,
                    offline=True,
                )

            saved_files = list(Path(temp_dir).glob("benchmark_*.json"))

        self.assertEqual(output["statistics"]["successful"], 1)
        self.assertEqual(len(saved_files), 1)


if __name__ == "__main__":
    unittest.main()
