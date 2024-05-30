import shutil
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from chevron import render

from .posts import Loader, Post, datetime_naïve
from .xml import Doc, Elt


@dataclass
class Link:
    rel: str
    href: str
    title: str | None = None
    type: str | None = None


class Gen:
    page_size = 12

    def __init__(self, tpl_dir: Path | str, static_dir: Path | str = None):
        self.tpl_dir = Path(tpl_dir)
        self.flush_tpls()
        if static_dir:
            self.static_dir = Path(static_dir)
        else:
            static_dir = self.tpl_dir.parent / "static"
            if static_dir.is_dir():
                self.static_dir = static_dir
            else:
                self.static_dir = None

    def flush_tpls(self):
        """Discard cached templates and reload."""
        self.templates = {
            self.fname(file): file.read_text()
            for file in self.tpl_dir.glob("**/*.mustache")
        }

    def render_posts(self, loader: Loader, public_path: Path | str):
        """Generate HTML files in the specified directory."""
        public_path = Path(public_path)
        if self.static_dir:
            shutil.copytree(self.static_dir, public_path, dirs_exist_ok=True)
        elif not public_path.exists():
            public_path.mkdir()

        for post in loader.posts():
            self._render_1(
                public_path, f"{post.name}.html", post.context(), "post.html"
            )
        self.render_index(loader, public_path)

        post_count = len(loader.posts())
        page_count = (post_count + self.page_size - 1) // self.page_size
        for i in range(page_count):
            feed_path = public_path / (self.feed_href(i + 1))
            with feed_path.open("w", encoding="UTF-8") as f:
                self._atom_feed(loader, page=(i + 1)).write_to(f)

    def render_index(self, loader: Loader, public_path: Path):
        links = [Link("alternate", self.feed_href(1), type="application/atom+xml")]
        self._render_1(
            public_path,
            "index.html",
            {
                "reverse_chronological": [
                    post.context() for post in reversed(loader.posts())
                ],
                "is_index": True,
                "links": links,
            },
        )

    def _render_1(
        self,
        public_path: Path,
        name: str,
        context: Mapping[str, Any],
        tpl_name: str = None,
    ):
        out_file = public_path / name
        html = render(
            self.templates[tpl_name or name], context, partials_dict=self.templates
        )
        out_file.write_text(html, encoding="UTF-8")

    def _atom_feed(self, loader: Loader, page: int) -> Doc:
        doc = Doc("atom:feed")
        posts = loader.posts()
        page_count = (len(posts) + self.page_size - 1) // self.page_size
        if page > 1:
            offset = (page - 1) * self.page_size
            posts = posts[-offset - self.page_size : -offset]
        else:
            posts = posts[-self.page_size :]
        posts.reverse()

        # Feed metadata comes first
        doc.element("atom:id", {}, loader.id)
        doc.element("atom:title", {}, loader.title)
        if url := loader.meta.get("url"):
            doc.element(
                "atom:link",
                {"rel": "self", "href": urljoin(url, self.feed_href(page))},
            )
            if page == 1:
                doc.element("atom:link", {"rel": "alternate", "href": url})

        if page > 1:
            doc.element(
                "atom:link",
                {"rel": "first", "href": self.feed_href(1)},
            )
            doc.element(
                "atom:link",
                {"rel": "previous", "href": self.feed_href(page - 1)},
            )
        if page < page_count:
            doc.element(
                "atom:link",
                {"rel": "next", "href": self.feed_href(page + 1)},
            )
            doc.element(
                "atom:link",
                {"rel": "last", "href": self.feed_href(page_count)},
            )

        updated = max(
            (p.meta.get("updated", p.meta["published"]) for p in posts),
            default=datetime(2024, 5, 5),
        )
        doc.element("atom:updated", {}, atom_date(updated))
        doc.element(
            "atom:generator",
            {"uri": "https://github.com/pdc/mismiy", "version": version("mismiy")},
            "Mismiy",
        )

        # Entries go at end.
        for post in posts:
            doc.append(self._atom_entry(loader, post))
        return doc

    def _atom_entry(self, loader: Loader, post: Post) -> Elt:
        result = Elt("atom:entry")
        result.element("atom:id", post.make_id(loader.id))
        result.element("atom:title", post.meta["title"])
        result.element("atom:published", atom_date(post.meta["published"]))
        updated = post.meta.get("updated") or post.meta["published"]
        result.element("atom:updated", atom_date(updated))
        if person := post.meta.get("author"):
            result.append(person.atom_person("atom:author"))
        result.element(
            "atom:link", {"rel": "alternate", "type": "text/html", "href": post.href}
        )
        result.element("atom:content", {"type": "html"}, post.body_html())
        return result

    def feed_href(self, page):
        return f"feed-{page}.xml" if page > 1 else "feed.xml"

    def fname(self, file: Path) -> str:
        return str(file.relative_to(self.tpl_dir)).removesuffix(".mustache")


def atom_date(d: datetime) -> str:
    # Atom does not allow timestamps without time zones.
    assert not datetime_naïve(d)
    return d.isoformat()
