from datetime import date, timedelta


def next_occurrence(current: date, frequency: str) -> date:
    """Compute the next occurrence date based on frequency."""
    if frequency == "daily":
        return current + timedelta(days=1)
    elif frequency == "weekly":
        return current + timedelta(weeks=1)
    elif frequency == "monthly":
        # Advance by one month, handling month-end edge cases
        month = current.month + 1
        year = current.year
        if month > 12:
            month = 1
            year += 1
        # Clamp day to valid range for the new month
        import calendar
        max_day = calendar.monthrange(year, month)[1]
        day = min(current.day, max_day)
        return date(year, month, day)
    elif frequency == "yearly":
        import calendar
        year = current.year + 1
        max_day = calendar.monthrange(year, current.month)[1]
        day = min(current.day, max_day)
        return date(year, current.month, day)
    else:
        raise ValueError(f"Unknown frequency: {frequency}")


def period_bounds(period_type: str, reference: date) -> tuple[date, date]:
    """Return (start, end) date bounds for the given period type containing reference date."""
    if period_type == "monthly":
        import calendar
        start = date(reference.year, reference.month, 1)
        last_day = calendar.monthrange(reference.year, reference.month)[1]
        end = date(reference.year, reference.month, last_day)
        return start, end
    elif period_type == "weekly":
        # Week starts on Monday
        start = reference - timedelta(days=reference.weekday())
        end = start + timedelta(days=6)
        return start, end
    elif period_type == "yearly":
        start = date(reference.year, 1, 1)
        end = date(reference.year, 12, 31)
        return start, end
    else:
        # custom — return just the reference day
        return reference, reference
