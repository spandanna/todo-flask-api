import datetime as dt
from typing import List


def get_dates(start_date: dt.date, interval: int, end_date: dt.date) -> List[(dt.date)]:
    """
    Returns a list of dates every `interval` days from the `start_date`
    until the `end_date`.
    """
    dates = [start_date]
    current_date = start_date
    while current_date < end_date:
        current_date += dt.timedelta(days=interval)
        dates.append(current_date)
    return dates
