import unittest
from tempfile import mkdtemp
from shutil import rmtree
from pathlib import Path

from mismiy.posts import Loader, Post


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

    def test_dotdotslash_if_slahes_in_namet(self):
        post = Post("2024/05/05/hello", {"title": "Hello"}, "Hello, *world*!")

        result = post.context()

        # Then the dotdotslash item is the path back to the root of the posts.
        self.assertEqual(result["dotdotslash"], "../../../")
