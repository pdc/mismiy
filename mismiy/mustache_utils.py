import locale
import re
from collections.abc import Callable, Mapping
from datetime import date, datetime


def expand_date(d: datetime | date) -> Mapping[str, str]:
    month_name = locale.nl_langinfo(getattr(locale, f"MON_{d.month}"))

    return {
        "year": str(d.year),
        "month": str(d.month),
        "month_2digits": "%02d" % d.month,
        "month_name": month_name,
        "day": str(d.day),
        "day_2digits": "%02d" % d.day,
        "iso_date": (d.date() if isinstance(d, datetime) else d).isoformat(),
        "iso_datetime": d.isoformat(),
    }


year_re = re.compile(r"\d{4}")


def as_date_lambda(text: str, render: Callable) -> str:
    """A mustache ‘lambda’ to convert context value to a date object.

    Exanmple: `{{#birthday}}{{#as_date}}{{day}} {{month_name}}{{/as_date}}{{/birthday}}`
    """
    # Get the date value:
    value = render("{{.}}")
    if isinstance(value, int) or year_re.match(value):
        # It’s just a year.
        data = {"year": int(value)}
    elif isinstance(value, str):
        value = (
            datetime.fromisoformat(value) if "T" in value else date.fromisoformat(value)
        )
        data = expand_date(value)
    else:
        data = expand_date(value)

    # Now render the section text with the expanded date.
    return render(text, data)


duration_pattern = re.compile(
    r"""
^P
(?: (?P<years>\d+)Y)?
(?: (?P<months>\d+)M)?
(?: (?P<days>\d+)D)?
(?:T
    (?: (?P<hours>\d+)H)?
    (?: (?P<minutes>\d+)M)?
    (?: (?P<seconds>\d+)S)?
)
$
""",
    re.VERBOSE,
)


def as_duration_lambda(text: str, render: Callable) -> str:
    """A mustache ‘lambda’ to convert context value to a date object.

    Exanmple: `{{#prep_time}}{{#as_duration}}{{hours}}:{{minutes}}{{/as_duration}}{{/prep_time}}`
    """
    # Get the date value:
    value = render("{{.}}")
    m = duration_pattern.match(value)
    if m:
        data = {
            key: int(value) for key, value in m.groupdict().items() if value is not None
        }
        return render(text, data)
    return text
