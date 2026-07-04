"""In-process coverage for the critique-artifact date fallbacks
(`scripts/validate_critique_artifacts.py`). ``tests/test_critique_artifact_validation.py``
and the ``quality_gates`` critique suites drive this module ONLY via
``subprocess.run(["python3", ...])``, so coverage.py never attributes lines
inside its date-parsing helpers. Both ``_date_from_filename`` and
``_date_from_body`` match a well-formed-looking date string with a regex and
then hand it to ``date.fromisoformat``, which can still reject an
out-of-range calendar date (e.g. month 13 or day 30 of February) -- the
``except ValueError: return None`` guard exists for exactly that gap between
"looked like a date" and "is a real date".
"""
from __future__ import annotations

from pathlib import Path

import scripts.validate_critique_artifacts as vca


def test_date_from_filename_returns_none_on_regex_match_but_invalid_calendar_date() -> None:
    # "2026-13-40" matches \d{4}-\d{2}-\d{2} but month 13 / day 40 do not exist.
    path = Path("2026-13-40-demo-critique.md")
    assert vca._date_from_filename(path) is None


def test_date_from_filename_reads_valid_leading_date() -> None:
    path = Path("2026-06-12-demo-critique.md")
    assert vca._date_from_filename(path) == vca.date(2026, 6, 12)


def test_date_from_body_returns_none_on_regex_match_but_invalid_calendar_date() -> None:
    # "Date: 2026-02-30" matches the line pattern but February has no 30th.
    text = "# Critique Review\nDate: 2026-02-30\n"
    assert vca._date_from_body(text) is None


def test_date_from_body_reads_valid_date_line() -> None:
    text = "# Critique Review\nDate: 2026-06-12\n"
    assert vca._date_from_body(text) == vca.date(2026, 6, 12)
