from datetime import datetime
import calendar


def get_month_range(year: int, month: int) -> tuple[int, int]:
    start = datetime(year, month, 1)
    end_day = calendar.monthrange(year, month)[1]
    end = datetime(year, month, end_day, 23, 59, 59)
    return int(start.timestamp()), int(end.timestamp())


def get_year_range(year: int) -> tuple[int, int]:
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31, 23, 59, 59)
    return int(start.timestamp()), int(end.timestamp())
