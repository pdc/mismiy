import locale
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, timezone, tzinfo
from pathlib import Path
from typing import Any, Self
from uuid import UUID, uuid5
from zoneinfo import ZoneInfo

import mistletoe
from strictyaml import Datetime, Email, Map, Optional, Str, Url
from strictyaml import load as yaml_load

from .xml import Elt

NAMESPACE_BLOG = UUID("30c72114-7908-4a69-84ff-7ed69090220d")

blank_line = re.compile(r"\s*\n\s*\n")
date_re = re.compile(r"^(20\d{2})-(\d{2})-(\d{2})")

person_schema = Str() | Map(
    {
        "name": Str(),
        Optional("uri"): Url(),
        Optional("email"): Email(),
    }
)
post_schema = Map(
    {
        "title": Str(),
        Optional("author"): person_schema,
        Optional("id"): Str(),
        Optional("published"): Datetime(),
        Optional("updated"): Datetime(),
    }
)
meta_schema = Map(
    {
        Optional("title"): Str(),
        Optional("id"): Str(),
        Optional("url"): Url(),
        Optional("tz"): Str(),
    }
)
# In the above, the `id` fields are `Str` rather than `Url` because
# the URL validator does not like URLs that start with `tag:` and `urn:`.


@dataclass
class Person:
    name: str
    uri: str | None = None
    email: str | None = None

    def atom_person(self, etype: str = "atom:author") -> Elt:
        result = Elt(etype)
        result.element("atom:name", self.name)
        if self.uri:
            result.element("atom:uri", self.uri)
        if self.email:
            result.element("atom:email", self.email)
        return result

    @classmethod
    def new(cls, obj: str | Mapping[str, str]) -> Self:
        if isinstance(obj, str):
            return cls(obj)
        return cls(**obj)


@dataclass
class Page:
    name: str
    meta: Mapping[str, Any]
    body: str

    @property
    def href(self):
        return f"{self.name}.html"

    @property
    def dotdotslash(self):
        return "".join(["../"] * (len(self.name.split("/")) - 1))

    def context(self):
        result = {
            k: expand_date(d) if isinstance(d, (datetime, date)) else d
            for k, d in self.meta.items()
        }
        result.update(
            {
                "name": self.name,
                "href": self.href,
                "dotdotslash": self.dotdotslash,
                "body": self.body_html(),
            }
        )
        return result

    def body_html(self):
        """The body of the entry, formatted as HTML fragment."""
        return mistletoe.markdown(self.body)

    def make_id(self, feed_id: str):
        """Given id of feed, create a unique id for this post."""
        if result := self.meta.get("id"):
            return result
        if feed_id.startswith("tag:") and "/" not in feed_id:
            colon = "" if feed_id.endswith(":") else ":"
            return f"{feed_id}{colon}{self.name}"
        if feed_id.startswith("urn:uuid"):
            namespace_uuid = feed_id.removeprefix("urn:uuid:")
            uuid = uuid5(UUID(namespace_uuid), self.name)
            return f"urn:uuid:{uuid}"
        slash = "" if feed_id.endswith("/") else "/"
        return f"{feed_id}{slash}{self.name}"

    @classmethod
    def from_text(cls, name: str, text: str, tz: tzinfo) -> "Page":
        """Create a post from this document.

        Arguments:
            name: names the post; usually filename without extension
            text: content of the post, with metadata separated from
                body by a bank line
            tz: the tzinfo value to use for published dates lacking
                a time zone
        """
        parts = blank_line.split(text, 1)
        if len(parts) != 2:
            raise ValueError("Expected meta and body separated by blank line.")
        meta = yaml_load(parts[0], post_schema).data
        if not meta.get("published") and (m := date_re.search(name)):
            meta["published"] = datetime(int(m[1]), int(m[2]), int(m[3]))
        for k, v in meta.items():
            if isinstance(v, datetime) and datetime_naïve(v):
                meta[k] = v.replace(tzinfo=tz)
        if obj := meta.get("author"):
            meta["author"] = Person.new(obj)
        return cls(name, meta, parts[1])

    @classmethod
    def from_file(cls, name: str, file: Path, tz: tzinfo) -> "Page":
        return cls.from_text(name, file.read_text(encoding="UTF-8"), tz)


def expand_date(d: datetime | date) -> Mapping[str, str]:
    month_name = locale.nl_langinfo(getattr(locale, f"MON_{d.month}"))
    return {
        "year": str(d.year),
        "month": str(d.month),
        "month_2digits": "%02d" % d.month,
        "month_name": month_name,
        "day": str(d.day),
        "day_2digits": "%02d" % d.day,
        "iso_date": d.date().isoformat(),
        "iso_datetime": d.isoformat(),
    }


class Source:
    """Loads posts from a directory full of Markdown files."""

    meta_file_name = "META.yaml"

    def __init__(
        self, pages_dir: Path | str, include_drafts=False, now: datetime | None = None
    ):
        self._meta = None
        self._pages = None
        self.pages_dir = Path(pages_dir)
        self.include_drafts = include_drafts
        self.now = now.astimezone(self.tz) if now else datetime.now(self.tz)

    @property
    def id(self):
        return self.meta["id"]

    @property
    def title(self):
        return self.meta["title"]

    @property
    def tz(self):
        return self.meta["tz"]

    @property
    def url(self):
        return self.meta["url"]

    @property
    def meta(self):
        """Metadata about the blog as a whole."""
        if self._meta is None:
            meta_file = self.pages_dir / self.meta_file_name
            if meta_file.exists():
                self._meta = yaml_load(meta_file.read_text(), meta_schema).data
                print("Loaded metadata from", meta_file)
            else:
                self._meta = {}
            # Ensure we have the minimum metadata.
            if not self._meta.get("id"):
                uuid = uuid5(NAMESPACE_BLOG, str(self.pages_dir.absolute()))
                self._meta["id"] = f"urn:uuid:{uuid}"
            if not self.meta.get("title"):
                p = self.pages_dir.absolute()
                while p.name == "posts":
                    p = p.parent
                self._meta["title"] = p.name
            if tz_name := self._meta.get("tz"):
                self._meta["tz"] = ZoneInfo(tz_name)
            else:
                self._meta["tz"] = timezone.utc
        return self._meta

    def flush(self):
        """Discard any cached posts, so next call to pages() loads them afresh."""
        self._pages = None

    def pages(self):
        if self._pages is None:
            self._pages = []
            for page_path in sorted(self.pages_dir.glob("**/*.markdown")):
                name = str(page_path.relative_to(self.pages_dir)).removesuffix(
                    ".markdown"
                )
                page = Page.from_file(name, page_path, tz=self.tz)

                published = page.meta.get("published")
                if published is None or published > self.now:
                    if self.include_drafts:
                        page.meta["is_draft"] = True
                    else:
                        continue
                self._pages.append(page)
        return self._pages


class Loader:
    def __init__(
        self,
        pages_dirs: list[Path | str],
        include_drafts=False,
        now: datetime | None = None,
    ):
        self.sources = [
            Source(pages_dir, include_drafts, now) for pages_dir in pages_dirs
        ]

    @property
    def id(self):
        """Id for use in feed."""
        for source in self.sources:
            if result := source.id:
                return result

    @property
    def title(self):
        """Title for use in feed."""
        for source in self.sources:
            if result := source.title:
                return result

    @property
    def tz(self):
        """Time zone for use in feed."""
        for source in self.sources:
            if result := source.tz:
                return result

    @property
    def url(self):
        """URL that is the base of the blog, used to generate links to posts."""
        for source in self.sources:
            if result := source.url:
                return result

    def flush(self):
        """Force all pages to be reloaded."""
        for source in self.sources:
            source.flush()

    def pages(self):
        return [p for source in self.sources for p in source.pages()]

    def posts(self):
        """Pages that have ‘post’ nature."""
        return self.pages()


def datetime_naïve(d: datetime) -> bool:
    return d.tzinfo is None or d.tzinfo.utcoffset(d) is None
