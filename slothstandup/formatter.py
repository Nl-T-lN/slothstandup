from typing import Dict, Any


class StandupFormatter:
    """Formats AI-generated standup data for Slack, Markdown, or Timesheets."""

    @staticmethod
    def to_slack(data: Dict[str, Any]) -> str:
        lines = [
            ":sloth: *Daily Standup Update*",
            "",
            ":white_check_mark: *Yesterday / Accomplished:*",
        ]
        for item in data.get("yesterday", []):
            lines.append(f"• {item}")

        lines.append("")
        lines.append(":construction: *Today / In Progress:*")
        for item in data.get("today", []):
            lines.append(f"• {item}")

        lines.append("")
        lines.append(":warning: *Blockers:*")
        for item in data.get("blockers", []):
            lines.append(f"• {item}")

        lines.append("")
        lines.append(f"_🦥 {data.get('sloth_quote', 'Sloth mode activated.')}_")
        return "\n".join(lines)

    @staticmethod
    def to_markdown(data: Dict[str, Any]) -> str:
        lines = [
            "### 🦥 Daily Standup Summary",
            "",
            "#### ✅ Yesterday",
        ]
        for item in data.get("yesterday", []):
            lines.append(f"- {item}")

        lines.append("")
        lines.append("#### 🚧 Today")
        for item in data.get("today", []):
            lines.append(f"- {item}")

        lines.append("")
        lines.append("#### 🚫 Blockers")
        for item in data.get("blockers", []):
            lines.append(f"- {item}")

        lines.append("")
        lines.append(f"> 💤 **Sloth Insight**: *{data.get('sloth_quote', 'Conserve energy.')}*")
        lines.append(f"> **Energy Conserved**: `{data.get('laziness_score', 95)}%`")
        return "\n".join(lines)

    @staticmethod
    def to_timesheet(data: Dict[str, Any]) -> str:
        lines = [
            "============================================================",
            "                   🦥 SLOTH TIMESHEET LOG                  ",
            "============================================================",
            f"{'Category':<20} | {'Task Description':<30} | {'Hours':<6}",
            "---------------------+--------------------------------+-------"
        ]
        total_hours = 0.0
        for entry in data.get("timesheet", []):
            cat = entry.get("category", "General")
            task = entry.get("task", "")[:28]
            hrs = float(entry.get("hours", 0.0))
            total_hours += hrs
            lines.append(f"{cat:<20} | {task:<30} | {hrs:>5.1f}h")

        lines.append("---------------------+--------------------------------+-------")
        lines.append(f"{'TOTAL LOGGED':<20} | {'':<30} | {total_hours:>5.1f}h")
        lines.append("============================================================")
        lines.append(f"Laziness Score: {data.get('laziness_score', 90)}% (Effort saved: 45 minutes)")
        return "\n".join(lines)
