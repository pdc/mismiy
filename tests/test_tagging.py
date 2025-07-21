import unittest

from mismiy.loader import Page
from mismiy.tagging import Tagging, TagInfo


class TestTagging(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.page_count = 0

    def test_adds_pages_indexed_by_tag(self):
        sut = Tagging()

        page1 = self.page_with_tags("Greet", ["greeting"])
        page2 = self.page_with_tags("Hi", ["thought"])
        page3 = self.page_with_tags("Hi", ["greeting"])
        sut.add(page1)
        sut.add(page2)
        sut.add(page3)

        self.assertEqual(sut.pages_for_terms(["greeting"]), [page1, page3])
        self.assertEqual(sut.pages_for_terms(["thought"]), [page2])

    def test_tags_are_matched_ignoring_case_and_whitespace(self):
        sut = Tagging()

        page1 = self.page_with_tags("Greet", ["Big Data"])
        page2 = self.page_with_tags("Hi", ["bigData"])
        page3 = self.page_with_tags("Hi", ["big data"])
        sut.add(page1)
        sut.add(page2)
        sut.add(page3)

        self.assertEqual(sut.pages_for_terms(["Big data"]), [page1, page2, page3])
        self.assertEqual(sut.pages_for_terms(["BIGDATA"]), [page1, page2, page3])

    def test_can_retrieve_tag_infos_for_heading(self):
        sut = Tagging()

        page1 = self.page_with_tags("Greet", ["greeting"])
        page2 = self.page_with_tags("Hi", ["Thought"])
        page3 = self.page_with_tags("Hi", ["Greeting"])
        sut.add(page1)
        sut.add(page2)
        sut.add(page3)

        # The labels are the most recent capitalization of the term.
        self.assertEqual(
            sut.tag_info("greeting"),
            TagInfo("Greeting", "tagged/greeting.html", 2),
        )
        self.assertEqual(
            sut.tag_info("thought"),
            TagInfo("Thought", "tagged/thought.html", 1),
        )

    def test_adds_pages_indexed_by_subsets_of_tags(self):
        sut = Tagging()

        page1 = self.page_with_tags("Why hello", ["greeting", "salutation", "hello"])
        sut.add(page1)

        self.assertEqual(
            sut.pages_for_terms(["greeting", "salutation", "hello"]), [page1]
        )
        self.assertEqual(sut.pages_for_terms(["salutation"]), [page1])
        self.assertEqual(sut.pages_for_terms(["greeting", "salutation"]), [page1])
        self.assertEqual(sut.pages_for_terms(["salutation", "hello"]), [page1])

    def test_supplies_tag_infos_for_page(self):
        # Given some pages have been tagged.
        sut = Tagging()
        page1 = self.page_with_tags("Apples", ["Fruit"])
        page2 = self.page_with_tags("Bananas", ["Fruit"])
        page3 = self.page_with_tags("Oranges", ["Fruit", "Colour", "Prince"])
        page4 = self.page_with_tags("Purples", ["Colour"])
        sut.add(page1)
        sut.add(page2)
        sut.add(page3)
        sut.add(page4)

        self.assertEqual(
            sut.page_tags(page1),
            [TagInfo("Fruit", "tagged/fruit.html", 3)],
        ),
        self.assertEqual(
            sut.page_tags(page3),
            [
                TagInfo("Fruit", "tagged/fruit.html", 3),
                TagInfo("Colour", "tagged/colour.html", 2),
                TagInfo("Prince", "tagged/prince.html", 1),
            ],
        )

    def test_can_list_narrowings_of_tags(self):
        sut = Tagging()
        page1 = self.page_with_tags("Alpha", ["Papa", "Quebec"])
        page2 = self.page_with_tags("Bravo", ["Quebec"])
        sut.add(page1)
        sut.add(page2)

        self.assertEqual(
            sut.narrowing_tags(["quebec"]),
            [TagInfo("Papa", "tagged/papa+quebec.html", 1)],
        )
        self.assertEqual(
            sut.narrowing_tags(["papa"]),
            [],
        )

    def test_can_list_widenings_of_tags(self):
        # Given some pages have been indexed.
        sut = Tagging()
        sut.add(self.page_with_tags("Alpha", ["Papa", "Quebec"]))
        sut.add(self.page_with_tags("Bravo", ["Quebec"]))
        sut.add(self.page_with_tags("Charley", ["Papa"]))
        sut.add(self.page_with_tags("Delta", ["Papa", "Romeo", "Quebec"]))
        sut.add(self.page_with_tags("Echo", ["Papa", "Quebec"]))
        sut.add(self.page_with_tags("Foxtrot", ["Papa"]))

        # Then widening gives resulting combination of tags.
        # They are sorted by increasing count.
        self.assertEqual(
            sut.widening_tags(["quebec", "papa"]),
            [
                TagInfo("Quebec", "tagged/quebec.html", 4),
                TagInfo("Papa", "tagged/papa.html", 5),
            ],
        )
        self.assertEqual(
            sut.widening_tags(["papa", "romeo", "quebec"]),
            [
                TagInfo("Papa + Quebec", "tagged/papa+quebec.html", 3),
                TagInfo("Quebec", "tagged/quebec.html", 4),
                TagInfo("Papa", "tagged/papa.html", 5),
            ],
        )

    def page_with_tags(self, title: str, tags: list[str]) -> Page:
        self.page_count += 1
        return Page(
            f"2025-03-{self.page_count:02d}-{title.lower().replace(' ', '-')}",
            {"title": title, "tags": tags},
            f"All about {title}!",
        )
