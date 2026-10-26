import unittest
from slothstandup.tabpfn_advisor import TabPFNAdvisor
from slothstandup.git_collector import GitActivity


class TestTabPFNAdvisor(unittest.TestCase):
    def setUp(self):
        self.advisor = TabPFNAdvisor()

    def test_sloth_nirvana(self):
        activity = GitActivity(repo_path=".", branch="main", stats={"insertions": 0, "deletions": 0, "files": 0})
        res = self.advisor.analyze_pacing(activity)
        self.assertFalse(res["anomaly_detected"])
        self.assertIn("Sloth", res["pacing_status"])

    def test_overexertion_anomaly(self):
        activity = GitActivity(repo_path=".", branch="main", stats={"insertions": 1200, "deletions": 300, "files": 25})
        res = self.advisor.analyze_pacing(activity)
        self.assertTrue(res["anomaly_detected"])
        self.assertIn("Overexertion", res["pacing_status"])


if __name__ == "__main__":
    unittest.main()
