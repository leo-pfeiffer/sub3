import datetime

from constants import SLOWEST_SUPPORTED_PACE


def get_first_day_of_week(dt: datetime.datetime) -> datetime.date:
    return (dt - datetime.timedelta(days=dt.weekday())).date()


def date_to_str(dt: datetime.date):
    return dt.strftime('%Y-%m-%d')


def m_to_km_or_mi(m: int, imperial=False):
    return m / 1000 if not imperial else m * 0.000621371


def lbs_to_kg(lbs: float):
    return lbs / 2.20462


def ms_to_min_km_or_min_mi(ms: int, imperial=False):
    if ms == 0:
        return SLOWEST_SUPPORTED_PACE
    if imperial:
        return 1609.34 / (ms * 60)
    return 1000 / (ms * 60)


def get_list_of_dates_between(start: datetime.datetime, end: datetime.datetime, delta: int):
    dates = []
    current = get_first_day_of_week(start)
    while current <= end.date():
        dates.append(current)
        current += datetime.timedelta(days=delta)
    return dates
