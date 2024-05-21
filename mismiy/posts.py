from dataclasses import dataclass
from datetime import datetime, date
from collections.abc import Mapping
import locale
from typing import Any
from pathlib import Path
import re
from strictyaml import load as yaml_load, Map, Str, Datetime, Optional
import mistletoe


blank_line = re.compile(r"\s*\n\s*\n")
date_re = re.compile(r"^(20\d{2})-(\d{2})-(\d{2})")

schema = Map({"title": Str(), Optional("published"): Datetime()})


@dataclass
class Post:
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
                "body": mistletoe.markdown(self.body),
            }
        )
        return result

    @classmethod
    def from_text(cls, name: str, text: str) -> "Post":
        parts = blank_line.split(text, 1)
        if len(parts) != 2:
            raise ValueError("Expected meta and body separated by blank line.")
        meta = yaml_load(parts[0], schema).data
        if not meta.get("published") and (m := date_re.search(name)):
            meta["published"] = datetime(int(m[1]), int(m[2]), int(m[3]))
        return cls(name, meta, parts[1])

    @classmethod
    def from_file(cls, name: str, file: Path) -> "Post":
        return cls.from_text(name, file.read_text(encoding="UTF-8"))


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
    }


class Loader:
    """Loads posts from a directory full of Markdown files."""

    def __init__(
        self,
        post_dir: Path | str,
        include_drafts=False,
        now: datetime | None = None,
    ):
        self.post_dir = Path(post_dir)
        self._posts = None
        self.include_drafts = include_drafts
        self.now = now or datetime.now()

    def flush(self):
        self._posts = None

    def posts(self):
        if self._posts is None:
            self._posts = []
            for post_path in sorted(self.post_dir.glob("**/*.markdown")):
                post = Post.from_file(
                    str(post_path.relative_to(self.post_dir)).removesuffix(".markdown"),
                    post_path,
                )

                published = post.meta.get("published")
                if published is None or published > self.now:
                    if self.include_drafts:
                        post.meta["is_draft"] = True
                    else:
                        continue
                self._posts.append(post)

        return self._posts

    def load(self, post_name):
        """Load the named post."""
        return Post.from_file(self.post_dir / (post_name + ".txt"))
