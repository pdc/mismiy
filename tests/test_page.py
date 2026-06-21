import unittest
from datetime import datetime
from uuid import UUID, uuid5

from mismiy.loader import Figure, Page
from mismiy.tagging import Tagging, TagInfo


class TestPage(unittest.TestCase):
    def test_renders_markdown(self):
        post = Page("2024-05-05--hello", {"title": "Hello"}, "Hello, *world*!")

        result = post.context()

        self.assertEqual(result["body_html"], "<p>Hello, <em>world</em>!</p>\n")

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

    def test_includes_data_json(self):
        page = Page(
            "2026-06-21-hello",
            {"title": "Hello", "data": {"@context": "https://schema.org/"}},
            "Hello, *world*!",
        )

        result = page.context()

        # Then the context includes data_json:
        self.assertEqual(
            result["data_json"],
            '{\n    "@context": "https://schema.org/"\n}',
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

    def test_dotdotslash_when_slahes_in_name(self):
        post = Page("2024/05/05/hello", {"title": "Hello"}, "Hello, *world*!")

        result = post.context()

        # Then the dotdotslash item is the path back to the root of the posts.
        self.assertEqual(result["dotdotslash"], "../../../")


class TestPageFigures(unittest.TestCase):
    def test_uses_src_and_srcset_if_supplied(self):
        page = Page(
            "2026/03/14/pi-day",
            {
                "figures": [
                    {
                        "id": "xyz",
                        "src": "foo.png",
                        "srcset": "foo.2x.png 2x, foo.3x.png 3x",
                        "width": 480,
                        "height": 270,
                    },
                ]
            },
            "Hello world",
        )

        result = page.context()

        # Then metadata fields are converted to HTML.
        actual = result["figures"][0]
        self.assertEqual(actual.id, "xyz")
        self.assertEqual(actual.src, "foo.png")
        self.assertEqual(actual.srcset, "foo.2x.png 2x, foo.3x.png 3x")
        self.assertEqual(actual.width, 480)
        self.assertEqual(actual.height, 270)
        # And the figures are also exposed indexed by id.
        self.assertEqual(result["figures_by_id"]["xyz"], actual)

    def test_renders_markdown_in_figure_caption_and_description(self):
        page = Page(
            "2026/03/14/pi-day",
            {
                "figures": [
                    {
                        "src": "foo.png",
                        "caption": "Football on **oranges**",
                        "description": "Twenty-two _tiny_ footballers playing a game on the surface of an orange.",
                    },
                ]
            },
            "Hello world",
        )

        result = page.context()

        # Then metadata fields are converted to HTML.
        actual = result["figures"][0]
        self.assertEqual(actual.caption_html, "Football on <strong>oranges</strong>")
        self.assertEqual(
            actual.description_html,
            "Twenty-two <em>tiny</em> footballers playing a game on the surface of an orange.",
        )

    def test_generates_srcset_from_multiple_src(self):
        page = Page(
            "2026/03/14/pi-day",
            {
                "figures": [
                    {
                        "src": {
                            "1x": "bar.600.png",
                            "2x": "bar.1200.png",
                            "3x": "bar.1800.png",
                        },
                    },
                ]
            },
            "Hello world",
        )

        result = page.context()

        # Then the 1x image is used for the src.
        self.assertEqual(result["figures"][0].src, "bar.600.png")
        # And the srcset combines all the other src entries.
        self.assertEqual(
            result["figures"][0].srcset, "bar.1800.png 3x, bar.1200.png 2x"
        )

    def test_invents_id_field_for_figures_lacking_one(self):
        page = Page(
            "2026/03/14/pi-day",
            {
                "figures": [
                    {"src": "foo.jpeg"},
                    {"id": "marzipan", "src": "bar.jpeg"},
                    {"src": "baz.jpeg"},
                ]
            },
            "Hello world",
        )

        result = page.context()

        # Then the figures without ids have ids invented.
        self.assertEqual(
            result["figures"],
            [
                Figure(id="fig1", src_by_res={"1x": "foo.jpeg"}),
                Figure(id="marzipan", src_by_res={"1x": "bar.jpeg"}),
                Figure(id="fig2", src_by_res={"1x": "baz.jpeg"}),
            ],
        )


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
