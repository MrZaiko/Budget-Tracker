"""Unit tests for date utilities."""

from datetime import date

import pytest

from app.utils.date_utils import next_occurrence, period_bounds


@pytest.mark.parametrize(
    "current, frequency, expected",
    [
        (date(2024, 1, 1), "daily", date(2024, 1, 2)),
        (date(2024, 1, 1), "weekly", date(2024, 1, 8)),
        (date(2024, 1, 31), "monthly", date(2024, 2, 29)),  # 2024 is leap year
        (date(2024, 1, 31), "yearly", date(2025, 1, 31)),
        (date(2024, 3, 31), "monthly", date(2024, 4, 30)),  # April has 30 days
        (date(2024, 2, 29), "yearly", date(2025, 2, 28)),  # non-leap year clamp
    ],
)
def test_next_occurrence(current: date, frequency: str, expected: date) -> None:
    assert next_occurrence(current, frequency) == expected


def test_next_occurrence_unknown_frequency() -> None:
    with pytest.raises(ValueError, match="Unknown frequency"):
        next_occurrence(date(2024, 1, 1), "hourly")


@pytest.mark.parametrize(
    "period_type, reference, expected_start, expected_end",
    [
        ("monthly", date(2024, 3, 15), date(2024, 3, 1), date(2024, 3, 31)),
        ("monthly", date(2024, 2, 10), date(2024, 2, 1), date(2024, 2, 29)),  # leap
        ("weekly", date(2024, 3, 13), date(2024, 3, 11), date(2024, 3, 17)),  # Wed → Mon-Sun
        ("yearly", date(2024, 7, 4), date(2024, 1, 1), date(2024, 12, 31)),
    ],
)
def test_period_bounds(
    period_type: str, reference: date, expected_start: date, expected_end: date
) -> None:
    start, end = period_bounds(period_type, reference)
    assert start == expected_start
    assert end == expected_end
