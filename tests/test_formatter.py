import unittest
from slothstandup.formatter import StandupFormatter


class TestStandupFormatter(unittest.TestCase):
    def setUp(self):
        self.sample_data = {
            "yesterday": ["Implemented auth middleware", "Fixed SQL query leak"],
            "today": ["Roll out caching layer"],
            "blockers": ["None"],
            "timesheet": [
                {"category": "Engineering", "task": "Auth middleware", "hours": 4.0},
                {"category": "Engineering", "task": "SQL query fix", "hours": 2.5}
            ],
            "sloth_quote": "Conserve calories, write clean code.",
            "laziness_score": 96
        }

    def test_to_slack(self):
        slack = StandupFormatter.to_slack(self.sample_data)
        self.assertIn(":sloth: *Daily Standup Update*", slack)
        self.assertIn("Implemented auth middleware", slack)
        self.assertIn("Conserve calories", slack)

    def test_to_markdown(self):
        md = StandupFormatter.to_markdown(self.sample_data)
        self.assertIn("### 🦥 Daily Standup Summary", md)
        self.assertIn("96%", md)

    def test_to_timesheet(self):
        ts = StandupFormatter.to_timesheet(self.sample_data)
        self.assertIn("SLOTH TIMESHEET LOG", ts)
        self.assertIn("6.5h", ts)


if __name__ == "__main__":
    unittest.main()
