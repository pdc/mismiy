import unittest
from datetime import datetime

from mismiy.gen import Gen
from mismiy.loader import Loader, Page, Person

from .mixins import TempDirMixin


class TestGen(TempDirMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.posts_dir = self.dir_path / "posts"
        self.posts_dir.mkdir()
        (self.posts_dir / "META.yaml").write_text(
            "id: tag:alleged.org.uk,2024:mismiy:test\n"
            "title: Test blog\n"
            "url: https://mismiy.example/test/\n"
            "tz: Europe/London\n"
        )

        self.pages_dir = self.dir_path / "pages"
        self.pages_dir.mkdir()

        self.tpl_dir = self.dir_path / "tpl"
        self.tpl_dir.mkdir()
        self.add_tpl("post.html", "Default post template")
        self.add_tpl("page.html", "Default page template")
        self.add_tpl("index.html", "Index template")

        self.pub_dir = self.dir_path / "pub"
        self.loader = Loader([self.posts_dir, self.pages_dir])

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
        gen.render_pages(self.loader, self.pub_dir)

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

    def test_render_page(self):
        self.add_page("about", "title: Hello\n\nHello, World!")
        self.add_tpl(
            "page.html",
            "<!DOCTYPE html><title>{{ title }}</title><body>\n"
            "<h1>{{ title }}</h1>\n"
            "{{{ body }}}\n"
            "{{> footer.html }}</body>\n",
        )
        self.add_tpl("footer.html", "<aside>Footer</aside>\n")

        gen = Gen(self.tpl_dir)
        gen.render_pages(self.loader, self.pub_dir)

        html_path = self.pub_dir / "about.html"
        self.assertTrue(html_path.exists())
        self.assertEqual(
            html_path.read_text(),
            "<!DOCTYPE html><title>Hello</title><body>\n"
            "<h1>Hello</h1>\n"
            "<p>Hello, World!</p>\n\n"
            "<aside>Footer</aside>\n"
            "</body>\n",
        )

    def test_renders_index_page(self):
        self.add_post("2024-05-05-hello", "title: Hello\n\nHello, World!")
        self.add_post("2024-05-06-hello", "title: Greetings\n\nGreetings, World!")
        self.add_tpl(
            "index.html",
            '{{#links}}<link rel={{rel}} href="{{href}}"{{#type}} type="{{type}}"{{/type}}>\n{{/links}}\n'
            "<ul>\n"
            "  {{# reverse_chronological }}\n"
            '  <li><a href="{{ href }}">{{ title }}</a></li>\n'
            "  {{/ reverse_chronological }}\n"
            "</ul>\n",
        )

        gen = Gen(self.tpl_dir)
        gen.render_pages(self.loader, self.pub_dir)

        # Then the index shows the most recent item first.
        html_path = self.pub_dir / "index.html"
        self.assertTrue(html_path.exists())
        self.assertEqual(
            html_path.read_text(),
            '<link rel=alternate href="feed.atom" type="application/atom+xml">\n'
            "<ul>\n"
            '  <li><a href="2024-05-06-hello.html">Greetings</a></li>\n'
            '  <li><a href="2024-05-05-hello.html">Hello</a></li>\n'
            "</ul>\n",
        )

    def test_renders_index_page_with_text(self):
        self.add_post("2024-05-05-hello", "title: Hello\n\nHello, World!")
        self.add_post("2024-05-06-hello", "title: Greetings\n\nGreetings, World!")
        self.add_tpl(
            "index.html",
            '{{#links}}<link rel={{rel}} href="{{href}}"{{#type}} type="{{type}}"{{/type}}>\n{{/links}}\n'
            "<article>\n"
            "{{{ body }}}</article>\n"
            "<ul>\n"
            "  {{# reverse_chronological }}\n"
            '  <li><a href="{{ href }}">{{ title }}</a></li>\n'
            "  {{/ reverse_chronological }}\n"
            "</ul>\n",
        )
        self.add_page("index", "title: Welcome\n\nHello, world!")

        gen = Gen(self.tpl_dir)
        gen.render_pages(self.loader, self.pub_dir)

        # Then the index shows the most recent item first.
        html_path = self.pub_dir / "index.html"
        self.assertTrue(html_path.exists())
        self.assertEqual(
            html_path.read_text(),
            '<link rel=alternate href="feed.atom" type="application/atom+xml">\n'
            "<article>\n"
            "<p>Hello, world!</p>\n"
            "</article>\n"
            "<ul>\n"
            '  <li><a href="2024-05-06-hello.html">Greetings</a></li>\n'
            '  <li><a href="2024-05-05-hello.html">Hello</a></li>\n'
            "</ul>\n",
        )

    def test_renders_static_files(self):
        static_dir = self.dir_path / "static"
        static_dir.mkdir()
        (static_dir / "man.css").write_text("body { font-family: Helvetica; }")

        gen = Gen(self.tpl_dir, static_dir)
        gen.render_pages(self.loader, self.pub_dir)

        self.assertEqual(
            (self.pub_dir / "man.css").read_text(), "body { font-family: Helvetica; }"
        )

    def test_skips_unpublished_posts(self):
        self.add_post("2024-05-19-drafty", "title: Drafty\n\nHello, world!")
        self.loader = Loader(
            [self.posts_dir], include_drafts=False, now=datetime(2024, 5, 18, 22, 18)
        )

        # When the site is generated before the publication date …
        gen = Gen(self.tpl_dir)
        gen.render_pages(self.loader, self.pub_dir)

        # Then the draft post is omitted.
        self.assertFalse((self.pub_dir / "2024-05-19-drafty.html").exists())
        # And there is no link from the index.
        self.assertNotRegex(
            (self.pub_dir / "index.html").read_text(), "2024-05-19-drafty.html"
        )

    def test_includes_unpublished_posts_if_drafts_mode(self):
        self.add_post("2024-05-19-drafty", "title: Drafty\n\nHello, world!")
        self.loader = Loader(
            [self.posts_dir], include_drafts=True, now=datetime(2024, 5, 18, 22, 18)
        )
        self.add_tpl(
            "index.html",
            '{{# reverse_chronological }}<a href="{{ href }}">{{ title }}</a>{{/ reverse_chronological }}',
        )

        # When the site is generated before the publication date with include_drafts true …
        gen = Gen(self.tpl_dir)
        gen.render_pages(self.loader, self.pub_dir)

        # Then the draft post is included.
        self.assertTrue((self.pub_dir / "2024-05-19-drafty.html").exists())
        # And there is a link from the index.
        index_html = (self.pub_dir / "index.html").read_text()
        self.assertRegex(index_html, r"2024-05-19-drafty\.html")

    def test_can_create_atom_entry(self):
        post = Page(
            "2024-05-25-atomic",
            {
                "title": "Atomic title",
                "published": datetime.fromisoformat("2024-05-25T00:00+01:00"),
                "author": Person("Alice de Winter", "https://dewinter.example/alice"),
            },
            "Atomic first paragraph.\n\nAtomic second paragraph.",
        )
        gen = Gen(self.tpl_dir)

        result = gen._atom_entry(self.loader, post)

        self.assertEqual(
            result.find("atom:id").text,
            "tag:alleged.org.uk,2024:mismiy:test:2024-05-25-atomic",
        )
        self.assertEqual(result.find("atom:title").text, "Atomic title")
        # Published is mandatory, and must have a timezone.
        # (Will have to check this test still works whe BST is over.)
        self.assertEqual(
            result.find("atom:published").text,
            "2024-05-25T00:00:00+01:00",
        )
        # Updated same as publiushed (until we add a way to upodate it)
        self.assertEqual(
            result.find("atom:updated").text,
            "2024-05-25T00:00:00+01:00",
        )
        self.assertEqual(
            result.find("atom:author").to_string(),
            "<atom:author>\n"
            "  <atom:name>Alice de Winter</atom:name>\n"
            "  <atom:uri>https://dewinter.example/alice</atom:uri>\n"
            "</atom:author>\n",
        )
        # The content is escaped HTML.
        self.assertEqual(
            result.find("atom:content").to_string(),
            '<atom:content type="html">&lt;p&gt;Atomic first paragraph.&lt;/p&gt;\n'
            "&lt;p&gt;Atomic second paragraph.&lt;/p&gt;\n"
            "</atom:content>\n",
        )
        # We assume feed.atom.xml is sibling to index.html
        self.assertEqual(
            result.find("atom:link", {"rel": "alternate"}).attrs,
            {"rel": "alternate", "href": "2024-05-25-atomic.html", "type": "text/html"},
        )

        # Future:
        # - Multiple authors
        # - Contrubutors
        # - Categories
        # - Summary (optional since we have content)

    def test_can_set_updated_in_metadata(self):
        post = Page(
            "2024-05-25-updated",
            {
                "title": "2024-05-25-updated title",
                "published": datetime.fromisoformat("2024-05-25T00:00+01:00"),
                "updated": datetime.fromisoformat("2024-05-26T17:48+01:00"),
                "author": Person("Bob McRobertson"),
            },
            "OK.",
        )
        gen = Gen(self.tpl_dir)

        result = gen._atom_entry(self.loader, post)

        self.assertEqual(result.find("atom:updated").text, "2024-05-26T17:48:00+01:00")

    def test_can_create_atom_feed(self):
        self.add_post("2024-05-24-fabulous", "title: Fabulous\n\nHello, world!")
        self.add_post(
            "2024-05-19-drafty", "title: Drafty\nupdated: 2024-05-26\n\nHello, world!"
        )

        gen = Gen(self.tpl_dir)
        result = gen._atom_feed(self.loader, page=1)

        # Then it is an XML doc with root `atom:feed`.
        self.assertEqual(result.etype, "atom:feed")
        self.assertEqual(
            result.find("atom:link", {"rel": "self"}).attrs["href"],
            "https://mismiy.example/test/feed.atom",
        )
        # And it has the required Atom feed elements.
        self.assertEqual(result.find("atom:id").text, self.loader.id)
        self.assertEqual(result.find("atom:title").text, self.loader.title)
        self.assertEqual(result.find("atom:updated").text, "2024-05-26T00:00:00+01:00")
        # And contains entries in reverse chronological order.
        self.assertEqual(
            [
                e.find("atom:title").text
                for e in result.elements
                if e.etype == "atom:entry"
            ],
            ["Fabulous", "Drafty"],
        )

    def test_limits_feed_to_12_entries(self):
        # Given 15 posts …
        for i in range(1, 26):
            self.add_post(
                f"2024-05-{i:02d}-hello", f"title: Greetings from {i} May 2024\n\nOK!"
            )
        # And the generateor page size is 12 …
        gen = Gen(self.tpl_dir)
        gen.page_size = 12

        result = gen._atom_feed(self.loader, page=1)

        # Then it has the most recent 12 posts
        self.assertEqual(
            [
                e.find("atom:title").text
                for e in result.elements
                if e.etype == "atom:entry"
            ],
            [f"Greetings from {i} May 2024" for i in range(25, 13, -1)],
        )
        self.assertEqual(
            result.find("atom:link", {"rel": "next"}).attrs["href"], "feed-2.atom"
        )
        self.assertEqual(
            result.find("atom:link", {"rel": "last"}).attrs["href"], "feed-3.atom"
        )

        # When we ask for page 2
        result = gen._atom_feed(self.loader, page=2)

        # Then it has the next most recent 12 posts
        self.assertEqual(
            [
                e.find("atom:title").text
                for e in result.elements
                if e.etype == "atom:entry"
            ],
            [f"Greetings from {i} May 2024" for i in range(13, 1, -1)],
        )
        self.assertEqual(
            result.find("atom:link", {"rel": "first"}).attrs["href"], "feed.atom"
        )
        self.assertEqual(
            result.find("atom:link", {"rel": "previous"}).attrs["href"], "feed.atom"
        )
        self.assertEqual(
            result.find("atom:link", {"rel": "next"}).attrs["href"], "feed-3.atom"
        )

    def test_render_feed(self):
        self.add_post("2024-05-05-hello", "title: Hello\n\nHello, World!")
        self.add_post("2024-05-06-hello", "title: Greetings\n\nGreetings, World!")

        gen = Gen(self.tpl_dir)
        gen.render_pages(self.loader, self.pub_dir)

        feed_file = self.pub_dir / "feed.atom"
        self.assertTrue(feed_file.exists())
        self.assertRegex(
            feed_file.read_text(),
            r'.*<feed xmlns="http://www.w3.org/2005/Atom">.*',
        )

    def add_post(self, name: str, text: str):
        (self.posts_dir / f"{name}.markdown").write_text(text)

    def add_page(self, name: str, text: str):
        (self.pages_dir / f"{name}.markdown").write_text(text)

    def add_tpl(self, name: str, text: str):
        (self.tpl_dir / f"{name}.mustache").write_text(text)
