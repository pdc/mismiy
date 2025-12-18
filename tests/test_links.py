import unittest

from mismiy.links import url_relative_to


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
