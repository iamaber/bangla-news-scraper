from datetime import date, timedelta


def date_range(start_date: date, end_date: date) -> list[date]:
    if end_date < start_date:
        return []
    total_days = (end_date - start_date).days
    return [start_date + timedelta(days=offset) for offset in range(total_days + 1)]
