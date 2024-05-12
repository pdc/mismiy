import unittest

from mismiy.posts import Loader
from mismiy.gen import Gen

from .test_posts_loader import TempDirMixin


class TestGen(TempDirMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.posts_dir = self.dir_path / "posts"
        self.posts_dir.mkdir()

        self.tpl_dir = self.dir_path / "tpl"
        self.tpl_dir.mkdir()
        self.add_tpl("post.html", "Post template")
        self.add_tpl("index.html", "Index template")

        self.pub_dir = self.dir_path / "pub"
        self.loader = Loader(self.posts_dir)

    def test_render_post(self):
        self.add_post("2024-05-05-hello", "title: Hello\n\nHello, World!")
        self.add_tpl(
            "post.html",
            "<!DOCTYPE html><title>{{ title }}</title><body>\n"
            "<h1>{{ title }}</h1>\n"
            "{{{ body }}}\n"
            "{{> footer.html }}</body>\n",
        )
        self.add_tpl("footer.html", "<aside>Footer</aside>\n")

        gen = Gen(self.tpl_dir)
        gen.render_posts(self.loader, self.pub_dir)

        html_path = self.pub_dir / "2024-05-05-hello.html"
        self.assertTrue(html_path.exists())
        self.assertEqual(
            html_path.read_text(),
            "<!DOCTYPE html><title>Hello</title><body>\n"
            "<h1>Hello</h1>\n"
            "<p>Hello, World!</p>\n\n"
            "<aside>Footer</aside>\n"
            "</body>\n",
        )

    def test_render_index(self):
        self.add_post("2024-05-05-hello", "title: Hello\n\nHello, World!")
        self.add_post("2024-05-06-hello", "title: Greetings\n\nGreetings, World!")
        self.add_tpl(
            "index.html",
            "<ul>\n"
            "  {{# reverse_chronological }}\n"
            '  <li><a href="{{ href }}">{{ title }}</a></li>\n'
            "  {{/ reverse_chronological }}\n"
            "</ul>\n",
        )

        gen = Gen(self.tpl_dir)
        gen.render_posts(self.loader, self.pub_dir)

        # Then the index shows the most recent item first.
        html_path = self.pub_dir / "index.html"
        self.assertTrue(html_path.exists())
        self.assertEqual(
            html_path.read_text(),
            '<ul>\n  <li><a href="2024-05-06-hello.html">Greetings</a></li>\n'
            '  <li><a href="2024-05-05-hello.html">Hello</a></li>\n</ul>\n',
        )

    def test_render_static(self):
        static_dir = self.dir_path / "static"
        static_dir.mkdir()
        (static_dir / "man.css").write_text("body { font-family: Helvetica; }")

        gen = Gen(self.tpl_dir, static_dir)
        gen.render_posts(self.loader, self.pub_dir)

        self.assertEqual(
            (self.pub_dir / "man.css").read_text(), "body { font-family: Helvetica; }"
        )

    def add_post(self, name: str, text: str):
        (self.posts_dir / f"{name}.markdown").write_text(text)

    def add_tpl(self, name: str, text: str):
        (self.tpl_dir / f"{name}.mustache").write_text(text)
