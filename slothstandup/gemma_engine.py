import os
import json
import requests
from typing import Dict, Any, Optional
from .git_collector import GitActivity


GEMMA_SYSTEM_PROMPT = """You are SlothStandup, an AI ghostwriter powered by Google's Gemma open-weight model.
You help exhausted, overworked developers maintain a calm, sloth-like peace of mind by turning their raw git commits, file changes, and branch activity into polished, professional daily standups and timesheet entries.

Guidelines:
1. Speak in a confident, highly competent engineering tone that shields the developer.
2. Group scattered commits into meaningful accomplishments.
3. Formulate realistic 'Yesterday', 'Today', and 'Blockers'.
4. Calculate realistic hours for timesheets (totaling ~6-8 hours).
5. Add a fun, dry-witted 'Sloth Wisdom' or 'Laziness Metric' celebrating energy conserved.
6. Return structured JSON with keys:
   - "yesterday": list of accomplishments
   - "today": list of planned tasks derived from current branch and active diffs
   - "blockers": list of blockers (default "None (clear skies)")
   - "timesheet": list of dicts with {"task": str, "hours": float, "category": str}
   - "sloth_quote": a witty sloth quote about saving developer energy
   - "laziness_score": integer percentage of energy conserved (e.g. 92)
"""


class GemmaEngine:
    """Orchestrates generation via open-weight Google Gemma models."""

    def __init__(
        self,
        model: str = "gemma2:2b",
        ollama_url: str = "http://localhost:11434",
        api_base: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.model = model
        self.ollama_url = os.getenv("OLLAMA_HOST", ollama_url).rstrip("/")
        self.api_base = api_base or os.getenv("OPENAI_BASE_URL") or os.getenv("GEMMA_API_BASE")
        self.api_key = api_key or os.getenv("GEMMA_API_KEY") or os.getenv("OPENAI_API_KEY")

    def _build_prompt(self, activity: GitActivity) -> str:
        commits_text = "\n".join(activity.commits) if activity.commits else "No formal commits made yet."
        uncommitted_text = "\n".join(activity.uncommitted_changes[:10]) if activity.uncommitted_changes else "Clean working tree."
        files_text = ", ".join(activity.changed_files[:15]) if activity.changed_files else "None"

        return f"""Analyze this developer's git activity and generate their standup update.

Current Branch: {activity.branch}
Stats: {activity.stats.get('insertions', 0)} insertions, {activity.stats.get('deletions', 0)} deletions across {activity.stats.get('files', 0)} files.
Recent Commits:
{commits_text}

Working Tree Staging:
{uncommitted_text}

Touched Files:
{files_text}

Output ONLY valid JSON matching the specified format:
{{
  "yesterday": ["item 1", "item 2"],
  "today": ["item 1", "item 2"],
  "blockers": ["None"],
  "timesheet": [{{"task": "Feature development", "hours": 4.5, "category": "Engineering"}}],
  "sloth_quote": "Moving slowly avoids breaking production.",
  "laziness_score": 94
}}
"""

    def generate(self, activity: GitActivity) -> Dict[str, Any]:
        """Attempt generation using local Ollama Gemma, custom API, or fallback heuristic."""
        # 1. Try local Ollama with Gemma
        try:
            res = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{GEMMA_SYSTEM_PROMPT}\n\n{self._build_prompt(activity)}",
                    "stream": False,
                    "format": "json"
                },
                timeout=12
            )
            if res.status_code == 200:
                data = res.json()
                raw_response = data.get("response", "")
                return self._parse_json(raw_response)
        except Exception:
            pass

        # 2. Try generic OpenAI-compatible API if configured
        if self.api_base and self.api_key:
            try:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": GEMMA_SYSTEM_PROMPT},
                        {"role": "user", "content": self._build_prompt(activity)}
                    ],
                    "temperature": 0.4
                }
                res = requests.post(f"{self.api_base}/chat/completions", json=payload, headers=headers, timeout=12)
                if res.status_code == 200:
                    raw_response = res.json()["choices"][0]["message"]["content"]
                    return self._parse_json(raw_response)
            except Exception:
                pass

        # 3. Intelligent Heuristic Engine (Gemma-aligned offline fallback)
        return self._fallback_generate(activity)

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        try:
            # strip markdown fences if present
            cleaned = raw_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except Exception:
            return self._fallback_generate(GitActivity(repo_path=".", branch="main"))

    def _fallback_generate(self, activity: GitActivity) -> Dict[str, Any]:
        """Provides a robust, witty, and contextual response if local Gemma daemon is cold."""
        yesterday_items = []
        if activity.commits:
            for c in activity.commits[:4]:
                parts = c.split("|")
                desc = parts[-1] if len(parts) > 1 else c
                yesterday_items.append(f"Delivered: {desc.capitalize()}")
        elif activity.uncommitted_changes:
            yesterday_items.append(f"Made progress on branch '{activity.branch}' across {len(activity.uncommitted_changes)} modified components.")
            yesterday_items.append("Refactored local modules and verified system stability.")
        else:
            yesterday_items.append(f"Investigated architectural improvements on branch '{activity.branch}'.")
            yesterday_items.append("Code review, backlog grooming, and system sanity verification.")

        today_items = [
            f"Continue feature rollout & integration on '{activity.branch}' branch.",
            "Write comprehensive tests, address edge cases, and run linting.",
            "Prepare PR for peer review once sanity checks pass."
        ]

        stats_ins = activity.stats.get("insertions", 0)
        timesheet = [
            {"task": f"Core feature implementation ({activity.branch})", "hours": 4.5, "category": "Engineering"},
            {"task": "Testing, debugging & local verification", "hours": 2.0, "category": "Quality Assurance"},
            {"task": "Architecture planning & code review", "hours": 1.0, "category": "Planning"}
        ]

        quotes = [
            "Never type in 15 minutes what an open-weight model can synthesize in 3 seconds.",
            "The fastest code is the code you didn't have to write, followed by the standup you didn't have to draft.",
            "Move slow, test steady, and preserve your biological battery.",
            "Why stress over status reports when Gemma has your back?"
        ]

        import random
        return {
            "yesterday": yesterday_items,
            "today": today_items,
            "blockers": ["None - clear progress."],
            "timesheet": timesheet,
            "sloth_quote": random.choice(quotes),
            "laziness_score": 93
        }
