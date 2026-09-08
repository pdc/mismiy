import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from functools import partial

from babel import Locale
from babel.numbers import format_decimal


@dataclass
class ExpandedDate:
    """Make partially digested date info available to Mustache template."""

    locale: Locale
    value: date | datetime

    @property
    def year(self):
        return str(self.value.year)

    @property
    def month(self):
        return str(self.value.month)

    @property
    def day(self):
        return str(self.value.day)

    @property
    def month_2digits(self):
        return "%02d" % self.value.month

    @property
    def day_2digits(self):
        return "%02d" % self.value.day

    @property
    def month_name(self):
        return self.locale.months["format"]["wide"][self.value.month]

    @property
    def iso_date(self):
        m = getattr(self.value, "date", None)
        d = m() if m else self.value
        return d.isoformat()

    @property
    def iso_datetime(self):
        return self.value.isoformat()


year_re = re.compile(r"^\d{4}$")


def locale_date_lambda(locale: Locale) -> Callable[[str, Callable], str]:
    expand_date = partial(ExpandedDate, locale)

    def as_date_lambda(text: str, render: Callable) -> str:
        """A mustache ‘lambda’ to convert context value to a date object.

        Example: `{{#birthday}}{{#as_date}}{{day}} {{month_name}}{{/as_date}}{{/birthday}}`
        """
        # Get the date value:
        value = render("{{.}}")
        # Since we are using this on data parsed by StrictYaml, in practice this
        # value will be a string, but let’s allow for actual values for future-proofing.
        if isinstance(value, int):
            # It’s just a year.
            data = {"year": str(value)}
        elif isinstance(value, (date, datetime)):
            data = expand_date(value)
        elif year_re.match(value):
            data = {"year": value}
        elif "T" in value:
            data = expand_date(datetime.fromisoformat(value))
        else:
            data = expand_date(date.fromisoformat(value))

        # Now render the section text with the expanded date.
        return render(text, data)

    return as_date_lambda


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


def locale_plural_lambda(locale: Locale):
    """Create Mustache lambda for rendering plural forms.

    The top of the context stack must be an integer.
    The content of the section is rendered with an object with
    the tag for the corresponding plural form set to true,
    and a field `number`
    """

    def plural_lambda(text: str, render: Callable) -> str:
        value = render("{{.}}")
        if isinstance(value, str):
            value = int(value)
        plural_tag = locale.plural_form(value)
        data = {
            "number": format_decimal(value, locale=locale),
            plural_tag: True,
        }
        return render(text, data)

    return plural_lambda
