import unittest
from datetime import datetime
from uuid import UUID, uuid5

from mismiy.loader import Page
from mismiy.tagging import Tagging, TagInfo


class TestPage(unittest.TestCase):
    def test_renders_markdown(self):
        post = Page("2024-05-05--hello", {"title": "Hello"}, "Hello, *world*!")

        result = post.context()

        self.assertEqual(result["body"], "<p>Hello, <em>world</em>!</p>\n")

    def test_includes_meta_in_context(self):
        page = Page(
            "2024-05-05--hello",
            {"title": "Hello"},
            "Hello, *world*!",
        )
        tagging = Tagging()
        tagging.add(page)

        result = page.context()

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

    def test_adds_tag_info_to_context_if_tagged(self):
        page = Page(
            "2024-05-05--hello",
            {"title": "Hello", "tags": ["Some tag"]},
            "Hello, *world*!",
        )
        tagging = Tagging()
        tagging.add(page)

        result = page.context(tagging)

        # Then the context includes at least the following items:
        self.assertEqual(
            result,
            result | {"tags": [TagInfo("Some tag", "tagged/sometag.html", 1)]},
        )

    def test_converts_datetime_to_dict(self):
        post = Page(
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

    def test_dotdotslash_if_slahes_in_name(self):
        post = Page("2024/05/05/hello", {"title": "Hello"}, "Hello, *world*!")

        result = post.context()

        # Then the dotdotslash item is the path back to the root of the posts.
        self.assertEqual(result["dotdotslash"], "../../../")


class TestPost(unittest.TestCase):
    def test_can_make_id_relative_to_uuid(self):
        post = Page("2024-05-25-hello", {"title": "Hello"}, "Hello, *world*!")

        self.assertEqual(
            post.make_id("urn:uuid:6f84b6fb-779e-5599-8a07-c133c2d6bd47"),
            f'urn:uuid:{uuid5(UUID("6f84b6fb-779e-5599-8a07-c133c2d6bd47"), "2024-05-25-hello")}',
        )

    def test_can_make_id_relative_to_tag(self):
        post = Page("2024-05-25-hello", {"title": "Hello"}, "Hello, *world*!")

        self.assertEqual(
            post.make_id("tag:alleged.org.uk,2024:mismiy:test"),
            "tag:alleged.org.uk,2024:mismiy:test:2024-05-25-hello",
        )

    def test_can_make_id_relative_to_http(self):
        post = Page("2024-05-25-hello", {"title": "Hello"}, "Hello, *world*!")

        self.assertEqual(
            post.make_id("http://some.example/foo/bar"),
            "http://some.example/foo/bar/2024-05-25-hello",
        )

    def test_treats_id_in_meta_as_canonical(self):
        post = Page(
            "2024-05-25-hello",
            {"title": "Hello", "id": "tag:alleged.org.uk,2024:mismiy:test:1234"},
            "Hello, *world*!",
        )

        self.assertEqual(
            post.make_id("http://some.example/foo/bar"),
            "tag:alleged.org.uk,2024:mismiy:test:1234",
        )
