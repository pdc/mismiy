import unittest
from datetime import datetime, timezone
from pathlib import Path

from mismiy.loader import Loader, Person, Source

from .mixins import TempDirMixin


class TestSource(TempDirMixin, unittest.TestCase):
    def test_pages_are_retrieved_in_file_name_order(self):
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
        source = Source(self.dir_path)

        result = source.pages()

        self.assertEqual(
            [post.meta["title"] for post in result],
            ["Vote", "Count", "Abacus", "Quince"],
        )
        self.assertEqual(result[0].body, "Hello, vote.")
        self.assertEqual(result[0].name, "2024-05-02-vote")

    def test_pages_have_optional_published_datetime(self):
        (self.dir_path / "2024-05-18-quince.markdown").write_text(
            "title: Greeting\npublished: 2024-05-19\n\nHello, world."
        )
        (self.dir_path / "2024-05-19-spum.markdown").write_text(
            "title: Greeting\n\nHello, world."
        )
        (self.dir_path / "undated.markdown").write_text(
            "title: Greeting\n\nHello, world."
        )
        source = Source(self.dir_path, include_drafts=True)

        result = source.pages()

        self.assertEqual(
            [post.meta.get("published") for post in result],
            [
                datetime(2024, 5, 19, tzinfo=timezone.utc),
                datetime(2024, 5, 19, tzinfo=timezone.utc),
                None,
            ],
        )

    def test_excludes_pages_published_in_future(self):
        # Given a page for a particular date …
        (self.dir_path / "2024-05-21-future.markdown").write_text(
            "title: Greeting\npublished: 2024-05-21\n\nHello, world."
        )

        # When we load pages before the post is published …
        source = Source(self.dir_path, now=datetime(2024, 5, 20, tzinfo=timezone.utc))
        result = source.pages()

        # Then we get an empty list because unpublished post omitted.
        self.assertFalse(result)

    def test_excludes_posts_without_published_date(self):
        # Given a post with no particular date …
        (self.dir_path / "undated.markdown").write_text(
            "title: Greeting\n\nHello, world."
        )
        (self.dir_path / "META.yaml").write_text("kind: post\n")

        # When we load pages before the post is published …
        source = Source(self.dir_path, now=datetime(2024, 6, 17, tzinfo=timezone.utc))
        result = source.pages()

        # Then we get an empty list because unpublished post omitted.
        self.assertFalse(result)

    def test_includes_undated_pages_though(self):
        # Given a page with no particular date …
        (self.dir_path / "undated.markdown").write_text(
            "title: Greeting\n\nHello, world."
        )
        (self.dir_path / "META.yaml").write_text("kind: page\n")

        # When we load pages before the post is published …
        source = Source(self.dir_path, now=datetime(2024, 6, 17, tzinfo=timezone.utc))
        result = source.pages()

        # Then page is not a draft (because it isn’t a post).
        self.assertFalse(result[0].meta.get("is_draft"))

    def test_includes_pages_if_caller_says_to_include_drafts(self):
        # Given a post for a particular date …
        (self.dir_path / "2024-05-21-future.markdown").write_text(
            "title: Greeting\npublished: 2024-05-21\n\nHello, world."
        )
        (self.dir_path / "undated.markdown").write_text(
            "title: Greeting\n\nWhat even is time?"
        )
        (self.dir_path / "META.yaml").write_text("kind: post\n")

        # When we load pages with the include_drafts flag …
        source = Source(
            self.dir_path,
            now=datetime(2024, 5, 20, tzinfo=timezone.utc),
            include_drafts=True,
        )
        result = source.pages()

        # Then we get draft posts.
        self.assertTrue(result[0].meta.get("is_draft"))
        self.assertTrue(result[1].meta.get("is_draft"))

    def test_allows_author_to_be_string(self):
        # Given a post with author supplied as just a string …
        (self.dir_path / "2024-05-25-greet.markdown").write_text(
            "title: Greeting\nauthor: Alice de Winter\n\nHello, world."
        )

        source = Source(self.dir_path)
        result = source.pages()

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

        source = Source(self.dir_path)
        result = source.pages()

        self.assertEqual(
            result[0].meta.get("author"),
            Person("Alice de Winter", "https://dewinter.example/alice"),
        )

    # Kinds of source (page or post):

    def test_random_directory_is_page(self):
        dir_path = self.dir_path / "banana_reviews"
        source = Source(dir_path)

        self.assertEqual(source.kind, "page")

    def test_posts_directory_is_post_kind(self):
        dir_path = self.dir_path / "posts"
        source = Source(dir_path)

        self.assertEqual(source.kind, "post")

    def test_can_set_source_kind_in_meta(self):
        dir_path = self.dir_path / "fred_gormghast"
        dir_path.mkdir()
        meta_file = dir_path / "META.yaml"
        meta_file.write_text("kind: post\n")
        source = Source(dir_path)

        self.assertEqual(source.kind, "post")

    def test_posts_acquire_kind_from_source(self):
        dir_path = self.dir_path / "posts"
        dir_path.mkdir()
        page_file = dir_path / "2024-06-17-hello.markdown"
        page_file.write_text("title: Hello\n\nHello, world\n")
        source = Source(dir_path)

        (page,) = source.pages()

        self.assertEqual(page.meta["kind"], "post")

    def test_pages_acquire_kind_from_source(self):
        dir_path = self.dir_path / "pages"
        dir_path.mkdir()
        page_file = dir_path / "hello.markdown"
        page_file.write_text("title: Hello\n\nHello, world\n")
        source = Source(dir_path)

        (page,) = source.pages()

        self.assertEqual(page.meta["kind"], "page")

    # Metadata needed for feed:

    def test_provides_blog_id_and_title(self):
        # Given a 2 blogs without meta files.
        posts_dir_1 = self.dir_path / "bananas/posts"
        posts_dir_1.mkdir(parents=True)
        posts_dir_2 = self.dir_path / "damsons"
        posts_dir_2.mkdir()

        # When we process these blogs …
        source_1 = Source(posts_dir_1)
        source_2 = Source(posts_dir_2)
        source_3 = Source(posts_dir_1)

        # Then title is guessed from the directory name.
        self.assertEqual(source_1.title, "bananas")
        self.assertEqual(source_2.title, "damsons")
        # And the sources have an id field.
        self.assertTrue(source_1.id)
        self.assertIsInstance(source_1.id, str)
        # And it is different for different directory names.
        self.assertNotEqual(source_2.id, source_1.id)
        self.assertEqual(source_1.id, source_3.id)

    def test_uses_absolute_path_when_guessing_title(self):
        # Given a blog with a relative file path …
        source = Source(Path("posts"))

        # Then it gets the title from the parent directory.
        self.assertTrue(source.title)

    def test_time_zone_defaults_to_utc(self):
        source = Source(self.dir_path)

        self.assertEqual(
            source.tz.tzname(datetime(2024, 5, 29, tzinfo=timezone.utc)), "UTC"
        )
        self.assertEqual(source.now.tzname(), "UTC")

    def test_reads_meta_yaml(self):
        meta_file = self.dir_path / "META.yaml"
        meta_file.write_text(
            "id: tag:dewinter.example,2024:alice\ntitle: Alice’s Awesome Blog\ntz: Australia/Brisbane\n"
        )

        source = Source(self.dir_path)

        self.assertEqual(source.id, "tag:dewinter.example,2024:alice")
        self.assertEqual(source.title, "Alice’s Awesome Blog")
        self.assertEqual(source.now.tzname(), "AEST")

    def test_assumes_naïve_now_is_local(self):

        source = Source(self.dir_path, now=datetime(2024, 5, 29, 22, 48))

        self.assertEqual(
            source.now,
            datetime(2024, 5, 29, 22, 48).astimezone(timezone.utc),
        )


class TestLoader(TempDirMixin, unittest.TestCase):
    """Loader wraps oneor mor sources."""

    def test_combines_pages_from_sources(self):
        # Given a 2 directories with pages in them…
        dir_1 = self.dir_path / "bananas/posts"
        dir_1.mkdir(parents=True)
        dir_2 = self.dir_path / "docs"
        dir_2.mkdir()
        (dir_1 / "2024-06-16-marzipan.markdown").write_text("title: Marzipan\n\nHello")
        (dir_2 / "about.markdown").write_text(
            "title: Creosote\npublished: 2024-06-16\n\nHello"
        )

        # When we process these blogs …
        loader = Loader([dir_1, dir_2])

        # Then we get a combined list of pages.
        self.assertCountEqual(
            [x.meta["title"] for x in loader.pages()],
            ["Marzipan", "Creosote"],
        )

    def test_combines_post_from_post_sources(self):
        # Given a 2 directories with pages in them…
        dir_1 = self.dir_path / "bananas/posts"
        dir_1.mkdir(parents=True)
        dir_2 = self.dir_path / "docs"
        dir_2.mkdir()
        (dir_1 / "2024-06-16-marzipan.markdown").write_text("title: Marzipan\n\nHello")
        (dir_2 / "about.markdown").write_text(
            "title: Creosote\npublished: 2024-06-16\n\nHello"
        )
        # And only one of them is posts …
        (dir_1 / "META.yaml").write_text("kind: post")

        # When we process these blogs …
        loader = Loader([dir_1, dir_2])

        # Then we get a posts from post sources.
        print(loader.posts())
        self.assertCountEqual(
            [x.meta["title"] for x in loader.posts()],
            ["Marzipan"],
        )
