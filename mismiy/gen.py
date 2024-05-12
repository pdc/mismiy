from pathlib import Path
from collections.abc import Mapping
import shutil
from typing import Any

from chevron import render

from .posts import Loader


class Gen:
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
        self.partials = {
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

    def render_index(self, loader: Loader, public_path: Path):
        self._render_1(
            public_path,
            "index.html",
            {
                "reverse_chronological": [
                    post.context() for post in reversed(loader.posts())
                ],
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
            self.partials[tpl_name or name], context, partials_dict=self.partials
        )
        out_file.write_text(html, encoding="UTF-8")

    def fname(self, file: Path) -> str:
        return str(file.relative_to(self.tpl_dir)).removesuffix(".mustache")
