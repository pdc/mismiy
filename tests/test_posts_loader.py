import unittest
from datetime import datetime
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp

from mismiy.posts import Loader, Person


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

    def test_allows_author_to_be_string(self):
        # Given a post with author supplied as just a string …
        (self.dir_path / "2024-05-25-greet.markdown").write_text(
            "title: Greeting\nauthor: Alice de Winter\n\nHello, world."
        )

        loader = Loader(self.dir_path)
        result = loader.posts()

        self.assertEqual(result[0].meta.get("author"), Person("Alice de Winter"))

    def test_allows_author_to_have_uri(self):
        # Given an author supplied as an object …
        (self.dir_path / "2024-05-25-greet.markdown").write_text(
            "title: Greeting\n"
            "author:\n"
            "  name: Alice de Winter\n"
            "  uri: https://dewinter.example/alice\n"
            "\n"
            "Hello, world.\n"
        )

        loader = Loader(self.dir_path)
        result = loader.posts()

        self.assertEqual(
            result[0].meta.get("author"),
            Person("Alice de Winter", "https://dewinter.example/alice"),
        )

    # Metadata needed for feed:

    def test_provides_blog_id_and_title(self):
        # Given a 2 blogs without meta files.
        posts_dir_1 = self.dir_path / "bananas/posts"
        posts_dir_1.mkdir(parents=True)
        posts_dir_2 = self.dir_path / "damsons"
        posts_dir_2.mkdir()

        # When we process these blogs …
        loader_1 = Loader(posts_dir_1)
        loader_2 = Loader(posts_dir_2)
        loader_3 = Loader(posts_dir_1)

        # Then title is guessed from the directory name.
        self.assertEqual(loader_1.title, "bananas")
        self.assertEqual(loader_2.title, "damsons")
        # And the loaders have an id field.
        self.assertTrue(loader_1.id)
        self.assertIsInstance(loader_1.id, str)
        # And it is different for different directory names.
        self.assertNotEqual(loader_2.id, loader_1.id)
        self.assertEqual(loader_1.id, loader_3.id)

    def test_uses_absolute_path_when_guessing_title(self):
        # Given a blog with a relative file path …
        loader = Loader(Path("posts"))

        # Then it gets the title from the parent directory.
        self.assertTrue(loader.title)

    def test_reads_meta_yaml(self):
        meta_file = self.dir_path / "META.yaml"
        meta_file.write_text(
            "id: tag:dewinter.example,2024:alice\ntitle: Alice’s Awesome Blog\n"
        )

        loader = Loader(self.dir_path)

        self.assertEqual(loader.id, "tag:dewinter.example,2024:alice")
        self.assertEqual(loader.title, "Alice’s Awesome Blog")
