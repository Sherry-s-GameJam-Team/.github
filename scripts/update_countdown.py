#!/usr/bin/env python3
"""Update the Game Jam development countdown block in README.md."""

from __future__ import annotations

import os
import re
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

README_PATH = Path("README.md")
START_DATE = date(2026, 7, 25)
END_DATE = date(2026, 8, 25)
TIMEZONE = "Asia/Shanghai"
BAR_WIDTH = 24

START_MARKER = "<!-- DEV_COUNTDOWN:START -->"
END_MARKER = "<!-- DEV_COUNTDOWN:END -->"


def get_today() -> date:
    """Return the local date, with an optional override for local testing."""
    override = os.getenv("TODAY_OVERRIDE")
    if override:
        try:
            return date.fromisoformat(override)
        except ValueError as exc:
            raise SystemExit(
                "TODAY_OVERRIDE must use YYYY-MM-DD, for example 2026-08-01."
            ) from exc

    return datetime.now(ZoneInfo(TIMEZONE)).date()


def build_countdown(today: date) -> str:
    total_days = (END_DATE - START_DATE).days + 1

    if today < START_DATE:
        days_until_start = (START_DATE - today).days
        status = f"距离开发开始还有 {days_until_start} 天"
        current_day = 0
        progress = 0
        display_date = today
    elif today <= END_DATE:
        remaining_days = (END_DATE - today).days
        status = (
            "今天是开发截止日"
            if remaining_days == 0
            else f"距离开发截止还有 {remaining_days} 天"
        )
        current_day = (today - START_DATE).days + 1
        progress = round(current_day / total_days * 100)
        display_date = today
    else:
        overdue_days = (today - END_DATE).days
        status = f"开发周期已结束 · 超出 {overdue_days} 天"
        current_day = total_days
        progress = 100
        # Freeze the rendered date after completion so the workflow
        # stops creating pointless daily commits.
        display_date = END_DATE

    filled = round(BAR_WIDTH * progress / 100)
    bar = "█" * filled + "░" * (BAR_WIDTH - filled)

    return f"""\
{START_MARKER}
<div align="center">

### `DEV // COUNTDOWN`

**{status}**

`DAY {current_day:02d} / {total_days:02d}` · `PROGRESS {progress:02d}%`

`{START_DATE:%Y.%m.%d}` `{bar}` `{END_DATE:%Y.%m.%d}`

<sub>自动更新于 {display_date:%Y.%m.%d} · {TIMEZONE}</sub>

</div>
{END_MARKER}"""


def update_readme() -> bool:
    if not README_PATH.exists():
        raise SystemExit(f"Cannot find {README_PATH}.")

    content = README_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        flags=re.DOTALL,
    )

    if not pattern.search(content):
        raise SystemExit(
            "Countdown markers were not found in README.md. "
            "Keep both DEV_COUNTDOWN markers in the file."
        )

    updated = pattern.sub(build_countdown(get_today()), content, count=1)

    if updated == content:
        print("README countdown is already up to date.")
        return False

    README_PATH.write_text(updated, encoding="utf-8")
    print("README countdown updated.")
    return True


if __name__ == "__main__":
    update_readme()
