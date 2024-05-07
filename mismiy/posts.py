from dataclasses import dataclass
from collections.abc import Mapping
from typing import Any
from pathlib import Path
import re
import strictyaml
import mistletoe


blank_line = re.compile(r"\s*\n\s*\n")


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
        body = mistletoe.markdown(self.body)
        return {
            **self.meta,
            "name": self.name,
            "href": self.href,
            "dotdotslash": self.dotdotslash,
            "body": body,
        }

    @classmethod
    def from_text(cls, name: str, text: str) -> "Post":
        parts = blank_line.split(text, 1)
        if len(parts) != 2:
            raise ValueError("Expected meta and body separated by blank line.")
        meta = strictyaml.load(parts[0]).data
        return cls(name, meta, parts[1])

    @classmethod
    def from_file(cls, name: str, file: Path) -> "Post":
        return cls.from_text(name, file.read_text(encoding="UTF-8"))


class Loader:
    def __init__(self, post_dir: Path | str):
        self.post_dir = Path(post_dir)
        self._posts = None

    def flush(self):
        self._posts = None

    def posts(self):
        if self._posts is not None:
            return self._posts
        post_paths = sorted(self.post_dir.glob("**/*.markdown"))
        self._posts = [
            Post.from_file(
                str(post_path.relative_to(self.post_dir)).removesuffix(".markdown"),
                post_path,
            )
            for post_path in post_paths
        ]
        return self._posts

    def load(self, post_name):
        """Load the named post."""
        return Post.from_file(self.post_dir / (post_name + ".txt"))
