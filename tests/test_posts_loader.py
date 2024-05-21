from datetime import datetime
import unittest
from tempfile import mkdtemp
from shutil import rmtree
from pathlib import Path

from mismiy.posts import Loader


class TempDirMixin:
    def setUp(self):
        super().setUp()
        self.test_dir = mkdtemp(prefix="TestPostsLoader")
        self.dir_path = Path(self.test_dir)

    def tearDown(self):
        rmtree(self.dir_path)
        super().tearDown()


class TestLoader(TempDirMixin, unittest.TestCase):
    def test_posts_are_retrieved_in_file_name_order(self):
        (self.dir_path / "2024-05-05-quince.markdown").write_text(
            "title: Quince\n\nHello, quince."
        )
        (self.dir_path / "2024-05-05-abacus.markdown").write_text(
            "title: Abacus\n\nHello, abacus."
        )
        (self.dir_path / "2024-05-02-vote.markdown").write_text(
            "title: Vote\n\nHello, vote."
        )
        (self.dir_path / "2024-05-03-count.markdown").write_text(
            "title: Count\n\nHello, count."
        )
        loader = Loader(self.dir_path)

        result = loader.posts()

        self.assertEqual(
            [post.meta["title"] for post in result],
            ["Vote", "Count", "Abacus", "Quince"],
        )
        self.assertEqual(result[0].body, "Hello, vote.")
        self.assertEqual(result[0].name, "2024-05-02-vote")

    def test_posts_have_optional_published_datetime(self):
        (self.dir_path / "2024-05-18-quince.markdown").write_text(
            "title: Greeting\npublished: 2024-05-19\n\nHello, world."
        )
        (self.dir_path / "2024-05-19-spum.markdown").write_text(
            "title: Greeting\n\nHello, world."
        )
        (self.dir_path / "undated.markdown").write_text(
            "title: Greeting\n\nHello, world."
        )
        loader = Loader(self.dir_path, include_drafts=True)

        result = loader.posts()

        self.assertEqual(
            [post.meta.get("published") for post in result],
            [datetime(2024, 5, 19), datetime(2024, 5, 19), None],
        )

    def test_excludes_posts_published_in_future(self):
        # Given a post for a particular date …
        (self.dir_path / "2024-05-21-future.markdown").write_text(
            "title: Greeting\npublished: 2024-05-21\n\nHello, world."
        )

        # When we load posts before the post is published …
        loader = Loader(self.dir_path, now=datetime(2024, 5, 20))
        result = loader.posts()

        # Then we get an empty list because unpublished post omitted.
        self.assertFalse(result)

    def test_includes_posts_if_include_drafts(self):
        # Given a post for a particular date …
        (self.dir_path / "2024-05-21-future.markdown").write_text(
            "title: Greeting\npublished: 2024-05-21\n\nHello, world."
        )

        # When we load posts before the post is published …
        loader = Loader(self.dir_path, now=datetime(2024, 5, 20), include_drafts=True)
        result = loader.posts()

        # Then we get an empty list because unpublished post omitted.
        self.assertTrue(result[0].meta.get("is_draft"))
