import unittest
import tempfile
import subprocess
import os
from slothstandup.git_collector import GitCollector, GitActivity


class TestGitCollector(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        # Initialize a temporary git repo
        subprocess.run(["git", "init", "-b", "main"], cwd=self.test_dir.name, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Nitin Pandey"], cwd=self.test_dir.name, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "nitinpandey11223@gmail.com"], cwd=self.test_dir.name, capture_output=True, check=True)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_empty_repo(self):
        collector = GitCollector(self.test_dir.name)
        self.assertTrue(collector.is_git_repo())
        activity = collector.collect()
        self.assertTrue(activity.is_empty)

    def test_repo_with_commit(self):
        sample_file = os.path.join(self.test_dir.name, "app.py")
        with open(sample_file, "w") as f:
            f.write("print('Hello Sloth')\n")
        
        subprocess.run(["git", "add", "."], cwd=self.test_dir.name, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "feat: initial commit for sloth"], cwd=self.test_dir.name, capture_output=True, check=True)

        collector = GitCollector(self.test_dir.name)
        activity = collector.collect(since="10 minutes ago")
        self.assertFalse(activity.is_empty)
        self.assertEqual(len(activity.commits), 1)
        self.assertIn("initial commit for sloth", activity.commits[0])


if __name__ == "__main__":
    unittest.main()
