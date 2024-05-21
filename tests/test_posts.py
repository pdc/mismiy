import unittest
from datetime import datetime

from mismiy.posts import Post


class TestPost(unittest.TestCase):
    def test_renders_markdown(self):
        post = Post("2024-05-05--hello", {"title": "Hello"}, "Hello, *world*!")

        result = post.context()

        self.assertEqual(result["body"], "<p>Hello, <em>world</em>!</p>\n")

    def test_includes_meta_in_context(self):
        post = Post("2024-05-05--hello", {"title": "Hello"}, "Hello, *world*!")

        result = post.context()

        # Then the context includes at least the following items:
        self.assertEqual(
            result,
            result
            | {
                "name": "2024-05-05--hello",
                "href": "2024-05-05--hello.html",
                "dotdotslash": "",
                "title": "Hello",
            },
        )

    def test_converts_datetime_to_dict(self):
        post = Post(
            "2024-05-19--hello",
            {
                "title": "Hello",
                "published": datetime(2024, 9, 7),
            },
            "Hello, *world*!",
        )

        result = post.context()

        # Then the context includes the date broken in to formatted parts.
        month_expected = datetime(2024, 9, 7).strftime("%B")
        self.assertEqual(
            result["published"],
            result["published"]
            | {
                "year": "2024",
                "month_name": month_expected,
                "month": "9",
                "month_2digits": "09",
                "day": "7",
                "day_2digits": "07",
                "iso_date": "2024-09-07",
            },
        )

    def test_dotdotslash_if_slahes_in_namet(self):
        post = Post("2024/05/05/hello", {"title": "Hello"}, "Hello, *world*!")

        result = post.context()

        # Then the dotdotslash item is the path back to the root of the posts.
        self.assertEqual(result["dotdotslash"], "../../../")
