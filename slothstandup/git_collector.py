import subprocess
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class GitActivity:
    repo_path: str
    branch: str
    commits: List[str] = field(default_factory=list)
    changed_files: List[str] = field(default_factory=list)
    uncommitted_changes: List[str] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=lambda: {"insertions": 0, "deletions": 0, "files": 0})
    is_empty: bool = False


class GitCollector:
    """Collects git activity, branch context, diffs, and commits from a local repository."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)

    def _run_git(self, args: List[str]) -> str:
        try:
            res = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return res.stdout.strip()
        except subprocess.CalledProcessError:
            return ""
        except FileNotFoundError:
            return ""

    def is_git_repo(self) -> bool:
        out = self._run_git(["rev-parse", "--is-inside-work-tree"])
        return out == "true"

    def get_current_branch(self) -> str:
        branch = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        return branch if branch else "main"

    def collect(self, since: str = "yesterday", author: Optional[str] = None) -> GitActivity:
        if not self.is_git_repo():
            return GitActivity(repo_path=self.repo_path, branch="none", is_empty=True)

        branch = self.get_current_branch()
        activity = GitActivity(repo_path=self.repo_path, branch=branch)

        # Collect commits
        git_log_args = ["log", f"--since={since}", "--pretty=format:%h|%an|%ar|%s"]
        if author:
            git_log_args.append(f"--author={author}")
        
        log_output = self._run_git(git_log_args)
        if log_output:
            for line in log_output.splitlines():
                if line.strip():
                    activity.commits.append(line.strip())

        # Collect shortstat for diffs since time
        stat_args = ["log", f"--since={since}", "--shortstat", "--oneline"]
        if author:
            stat_args.append(f"--author={author}")
        stat_out = self._run_git(stat_args)
        
        # Parse insertions / deletions / files changed
        insertions = 0
        deletions = 0
        files = 0
        for line in stat_out.splitlines():
            if "file" in line:
                parts = line.split(",")
                for p in parts:
                    p = p.strip()
                    if "file" in p:
                        try:
                            files += int(p.split()[0])
                        except ValueError:
                            pass
                    elif "insertion" in p:
                        try:
                            insertions += int(p.split()[0])
                        except ValueError:
                            pass
                    elif "deletion" in p:
                        try:
                            deletions += int(p.split()[0])
                        except ValueError:
                            pass

        activity.stats = {
            "files": files,
            "insertions": insertions,
            "deletions": deletions
        }

        # Collect uncommitted changes
        status_out = self._run_git(["status", "--porcelain"])
        if status_out:
            for line in status_out.splitlines():
                if line.strip():
                    activity.uncommitted_changes.append(line.strip())

        # Collect list of changed files
        files_out = self._run_git(["log", f"--since={since}", "--name-only", "--pretty=format:"])
        unique_files = set(f.strip() for f in files_out.splitlines() if f.strip())
        activity.changed_files = sorted(list(unique_files))

        if not activity.commits and not activity.uncommitted_changes:
            activity.is_empty = True

        return activity
