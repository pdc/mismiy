import unittest
from datetime import date, datetime
from unittest.mock import MagicMock, call
from zoneinfo import ZoneInfo

from mismiy.mustache_utils import as_date_lambda, as_duration_lambda, expand_date


class TestAsDate(unittest.TestCase):
    # These tests call the lambda function with a parameter that us the content
    # of the tag, a partial template, and a mocked render function.

    def test_converts_string_date_to_date(self):
        render = MagicMock(side_effect=["2026-07-04", "*rendered*"])

        result = as_date_lambda("*partial*", render)

        render.assert_has_calls(
            [
                call("{{.}}"),
                call("*partial*", expand_date(date(2026, 7, 4))),
            ]
        )
        self.assertEqual(result, "*rendered*")

    def test_converts_string_datetime_to_datetime(self):
        dt = datetime(2026, 7, 4, 12, 32, 45, tzinfo=ZoneInfo("Europe/London"))
        render = MagicMock(side_effect=[dt.isoformat(), "*rendered*"])

        result = as_date_lambda("*partial*", render)

        render.assert_has_calls(
            [
                call("{{.}}"),
                call("*partial*", expand_date(dt)),
            ]
        )
        self.assertEqual(result, "*rendered*")

    def test_expands_date(self):
        d = date(2026, 7, 5)
        render = MagicMock(side_effect=[d, "*rendered*"])

        result = as_date_lambda("*partial*", render)

        render.assert_has_calls(
            [
                call("{{.}}"),
                call("*partial*", expand_date(d)),
            ]
        )
        self.assertEqual(result, "*rendered*")

    def test_expands_year(self):
        # Given the data has a date value that is just the year …
        render = MagicMock(side_effect=["2026", "*rendered*"])

        result = as_date_lambda("*partial*", render)

        # Then the partial template is rendered with just the year provided.
        render.assert_has_calls(
            [
                call("{{.}}"),
                call("*partial*", {"year": 2026}),
            ]
        )
        self.assertEqual(result, "*rendered*")

    def test_expands_year_when_int(self):
        # Given the data has a date value that is just the year …
        render = MagicMock(side_effect=[2026, "*rendered*"])

        result = as_date_lambda("*partial*", render)

        # Then the partial template is rendered with just the year provided.
        render.assert_has_calls(
            [
                call("{{.}}"),
                call("*partial*", {"year": 2026}),
            ]
        )
        self.assertEqual(result, "*rendered*")


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
