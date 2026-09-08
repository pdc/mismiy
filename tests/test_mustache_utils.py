import unittest
from datetime import date, datetime
from unittest.mock import MagicMock, call
from zoneinfo import ZoneInfo

from babel import Locale

from mismiy.mustache_utils import (
    ExpandedDate,
    as_duration_lambda,
    locale_date_lambda,
    locale_plural_lambda,
)


class TestExpandedDate(unittest.TestCase):
    def test_expands_date_when_english(self):
        result = ExpandedDate(Locale("en", "GB"), date(2026, 9, 6))

        self.assertEqual(result.year, "2026")
        self.assertEqual(result.month, "9")
        self.assertEqual(result.month_2digits, "09")
        self.assertEqual(result.month_name, "September")
        self.assertEqual(result.day, "6")
        self.assertEqual(result.day_2digits, "06")
        self.assertEqual(result.iso_date, "2026-09-06")

    def test_expands_datetime_when_english(self):
        result = ExpandedDate(Locale("en", "GB"), datetime(2026, 9, 6, 18, 52, 41))

        self.assertEqual(result.year, "2026")
        self.assertEqual(result.month, "9")
        self.assertEqual(result.month_2digits, "09")
        self.assertEqual(result.month_name, "September")
        self.assertEqual(result.day, "6")
        self.assertEqual(result.day_2digits, "06")
        self.assertEqual(result.iso_date, "2026-09-06")
        self.assertEqual(result.iso_datetime, "2026-09-06T18:52:41")

    def test_uses_locale_when_greek(self):
        result = ExpandedDate(Locale("fr", "FR"), date(2026, 9, 6))

        self.assertEqual(result.month_name, "septembre")


class TestAsDate(unittest.TestCase):
    # These tests call the lambda function with a parameter that us the content
    # of the tag, a partial template, and a mocked render function.

    def test_converts_string_date_to_date(self):
        # Given the en-GB locale …
        locale = Locale("en", "GB")
        as_date_lambda = locale_date_lambda(locale)
        # And the template context is a stringified date …
        render = MagicMock(side_effect=["2026-07-04", "*rendered*"])

        result = as_date_lambda("*partial*", render)

        # Then the template is rendered with the expanded date.
        render.assert_has_calls(
            [
                call("{{.}}"),
                call("*partial*", ExpandedDate(locale, date(2026, 7, 4))),
            ]
        )
        self.assertEqual(result, "*rendered*")

    def test_converts_string_datetime_to_datetime(self):
        # Given a locale …
        locale = Locale("en", "GB")
        as_date_lambda = locale_date_lambda(locale)
        dt = datetime(2026, 7, 4, 12, 32, 45, tzinfo=ZoneInfo("Europe/London"))
        # And the template context is a stringified datetime …
        render = MagicMock(side_effect=[dt.isoformat(), "*rendered*"])

        as_date_lambda("*partial*", render)

        render.assert_called_with("*partial*", ExpandedDate(locale, dt))

    def test_expands_date(self):
        # Given a locale …
        locale = Locale("en", "GB")
        as_date_lambda = locale_date_lambda(locale)
        # And the template context is a date object …
        d = date(2026, 7, 5)
        render = MagicMock(side_effect=[d, "*rendered*"])

        as_date_lambda("*partial*", render)

        render.assert_called_with("*partial*", ExpandedDate(locale, d))

    def test_expands_year(self):
        # Given a locale …
        as_date_lambda = locale_date_lambda(Locale("en", "GB"))
        # And the data has a date value that is just the stringified year …
        render = MagicMock(side_effect=["2026", "*rendered*"])

        as_date_lambda("*partial*", render)

        # Then the partial template is rendered with just the year provided.
        render.assert_called_with("*partial*", {"year": "2026"})

    def test_expands_year_when_int(self):
        # Given a locale …
        as_date_lambda = locale_date_lambda(Locale("en", "GB"))
        # And the data has a date value that is just the year …
        render = MagicMock(side_effect=[2026, "*rendered*"])

        as_date_lambda("*partial*", render)

        # Then the partial template is rendered with just the year provided.
        render.assert_called_with("*partial*", {"year": "2026"})


class TestAsDuration(unittest.TestCase):
    def test_converts_time_frags(self):
        render = MagicMock(side_effect=["PT1H30M", "*rendered*"])

        result = as_duration_lambda("*partial*", render)

        render.assert_has_calls(
            [
                call("{{.}}"),
                call(
                    "*partial*",
                    {"hours": 1, "minutes": 30},
                ),
            ]
        )
        self.assertEqual(result, "*rendered*")

    def test_converts_date_durations(self):
        render = MagicMock(side_effect=["P3Y1M4DT1H5M9S", "*rendered*"])

        result = as_duration_lambda("*partial*", render)

        render.assert_has_calls(
            [
                call("{{.}}"),
                call(
                    "*partial*",
                    {
                        "years": 3,
                        "months": 1,
                        "days": 4,
                        "hours": 1,
                        "minutes": 5,
                        "seconds": 9,
                    },
                ),
            ]
        )
        self.assertEqual(result, "*rendered*")


class TestPlural(unittest.TestCase):
    def test_is_one_when_count_is_1(self):
        # Given plural_lambda has been bound to English locale …
        plural_lambda = locale_plural_lambda(Locale("en", "GB"))
        # And top of context stack is a number…
        render = MagicMock(side_effect=[1, "*rendered*"])

        result = plural_lambda("*partial*", render)

        # Then it returns the result of rendering with fields `one` and `number`.
        render.assert_has_calls(
            [call("{{.}}"), call("*partial*", {"one": True, "number": "1"})]
        )
        self.assertEqual(result, "*rendered*")

    def test_is_other_when_count_is_10(self):
        # Given the count is 10 …
        plural_lambda = locale_plural_lambda(Locale("en", "GB"))
        render = MagicMock(side_effect=[10, "*rendered*"])

        plural_lambda("*partial*", render)

        # Then it has a `other` field and no `one` field.
        render.assert_called_with("*partial*", {"other": True, "number": "10"})

    def test_localizes_the_number(self):
        # Given the count is 69420 …
        plural_lambda = locale_plural_lambda(Locale("en", "GB"))
        render = MagicMock(side_effect=[69420, "*rendered*"])

        plural_lambda("*partial*", render)

        # Then the number field has comma separating thousands.
        render.assert_called_with("*partial*", {"other": True, "number": "69,420"})

    def test_handles_stringified_numbers(self):
        # Given plural_lambda has been bound to English locale …
        plural_lambda = locale_plural_lambda(Locale("en", "GB"))
        # And top of context stack is a number…
        render = MagicMock(side_effect=["3", "*rendered*"])

        plural_lambda("*partial*", render)

        render.assert_called_with("*partial*", {"other": True, "number": "3"})
