import unittest

from mismiy.links import Link, munged, url_relative_to


class TestUrlRelativeTo(unittest.TestCase):

    def test_url_relative_itself_is_last_word(self):
        target = "alpha/bravo/charley.html"
        self.assertEqual(
            url_relative_to(target, target),
            "charley.html",
        )

    def test_common_prefix_discarded(self):
        target = "alpha/bravo/charley.html"
        base = "alpha/bravo/delta.html"
        self.assertEqual(
            url_relative_to(target, base),
            "charley.html",
        )

    def test_remaining_prefix_elements_imply_dotdot_slash(self):
        target = "alpha/bravo/charley.html"
        base = "alpha/delta/echo.html"
        self.assertEqual(
            url_relative_to(target, base),
            "../bravo/charley.html",
        )

    def test_can_dotdot_slash_to_top_of_common_hierarchy(self):
        target = "alpha/bravo/charley.html"
        base = "delta/echo/foxtrot/golf.html"
        self.assertEqual(
            url_relative_to(target, base),
            "../../../alpha/bravo/charley.html",
        )


class TestMungeLink(unittest.TestCase):

    def test_munged_without_parameters_returns_self(self):
        input = Link("first", "first.html", "First")

        # When munged with default parameters …
        result = munged(input, omit_dot_html=False)

        # Then it returns itself unmodified.
        self.assertIs(result, input)

    def test_munged_with_omit_html_omits_html(self):
        input = Link("first", "first-page.html", "First")

        # When munged with default parameters …
        result = munged(input, omit_dot_html=True)

        # Then it returns a link with shorter `href`.
        self.assertEqual(result, Link("first", "first-page", "First"))

    def test_munged_does_not_strip_other_suffixes(self):
        input = Link("feed", "feed.atom", "Atom feed")

        # When munged with default parameters …
        result = munged(input, omit_dot_html=True)

        # Then it returns itself unmodified.
        self.assertIs(result, input)
