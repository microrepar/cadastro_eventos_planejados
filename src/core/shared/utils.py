import datetime


def date_to_string(date: datetime.date) -> str:
    if date is not None:
        return str(date)