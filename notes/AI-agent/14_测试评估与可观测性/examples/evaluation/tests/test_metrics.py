import unittest

from metrics import (
    argument_exact_match,
    fact_coverage,
    percentile,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


class MetricTests(unittest.TestCase):
    def test_retrieval_metrics(self):
        retrieved = ["noise", "doc-b", "doc-a"]
        relevant = ["doc-a", "doc-b"]
        self.assertEqual(1.0, recall_at_k(retrieved, relevant, 3))
        self.assertAlmostEqual(2 / 3, precision_at_k(retrieved, relevant, 3))
        self.assertEqual(0.5, reciprocal_rank(retrieved, relevant))

    def test_duplicate_retrieval_does_not_inflate_score(self):
        self.assertEqual(0.5, recall_at_k(["doc-a", "doc-a"], ["doc-a", "doc-b"], 3))

    def test_fact_coverage_is_an_explainable_baseline(self):
        answer = "检索失败会缺少证据，所以检索和生成应分开评估。"
        facts = ["缺少证据", "分开评估"]
        self.assertEqual(1.0, fact_coverage(answer, facts))

    def test_argument_contract_and_percentile(self):
        self.assertEqual(1.0, argument_exact_match({"city": "上海"}, {"city": "上海"}))
        self.assertEqual(5, percentile([1, 2, 3, 4, 5], 0.95))


if __name__ == "__main__":
    unittest.main()
