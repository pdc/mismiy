import locale
import shutil
import sys
import time
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from strictyaml import Bool, Map, Optional, Str, UniqueSeq
from strictyaml import load as yaml_load
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from mismiy.gen import Gen
from mismiy.loader import Loader

# The schema for `mismiy-config.yaml`
config_schema = Map(
    {
        Optional("pages_dirs"): UniqueSeq(Str()),
        Optional("static_dir"): Str(),
        Optional("templates_dir"): Str(),
        Optional("out_dir"): Str(),
        Optional("omit_dot_html", default=False): Bool(),
        Optional("locale"): Str(),
    }
)


@dataclass
class Config:
    """Settings that are probably the same between runs.

    Not descriptions of the blog itself—that goes in META.yaml.
    """

    pages_dirs: list[Path]
    static_dir: Path
    templates_dir: Path
    out_dir: Path = "pub"
    omit_dot_html: bool = False
    locale: str = ""

    @classmethod
    def from_arguments(cls, args: Namespace):
        """Given command-line arguments, return a Config object.

        This also loads the configuration file, if any.
        This will have the settings from the arguments,  from the
        config file, and from the application defaults (in order
        from most to lowest priority).
        """

        config_file = Path("mismiy-config.yaml")
        if config_file.exists():
            defaults = yaml_load(config_file.read_text(), config_schema).data
        else:
            defaults = {}

        return Config(
            pages_dirs=[
                Path(d)
                for d in args.pages_dirs or defaults.get("pages_dirs") or ("posts",)
            ],
            static_dir=Path(args.static_dir or defaults.get("static_dir") or "static"),
            templates_dir=Path(
                args.templates_dir or defaults.get("templates_dir") or "templates"
            ),
            out_dir=Path(args.out_dir or defaults.get("out_dir") or "pub"),
            omit_dot_html=args.omit_dot_html
            if args.omit_dot_html is not None
            else defaults.get("omit_dot_html") or False,
            locale=args.locale or defaults.get("locale") or "",
        )

    @staticmethod
    def add_arguments(arg_parser: ArgumentParser):
        """Add the arguments for config options."""

        arg_parser.add_argument(
            "--templates-dir",
            "-t",
            metavar="PATH",
            help="Directory containing mustache templates. Default is `templates`.",
        )
        arg_parser.add_argument(
            "--static-dir",
            "-s",
            metavar="PATH",
            help="Root of static files. Default is `static`.",
        )
        arg_parser.add_argument(
            "--out-dir",
            "-o",
            metavar="PATH",
            help="Root of generated HTML tree. Default is `pub`.",
        )
        arg_parser.add_argument(
            "pages_dirs",
            metavar="PATH",
            nargs="*",
            help="A directory with posts or pages. My be repeated. Default is just posts.",
        )
        arg_parser.add_argument(
            "--omit-dot-html",
            action="store_true",
            default=None,
            help="Omit the .html suffix from href attributes",
        )
        arg_parser.add_argument(
            "--locale",
            metavar="LOCALE",
            help="Override the default locale. "
            "Must be a locale specifier like `en_GB.UTF-8`.",
        )


class GeneratingEventHandler(FileSystemEventHandler):
    def __init__(self, gen: Gen, loader: Loader, out_dir: Path):
        self.loader = loader
        self.gen = gen
        self.out_dir = out_dir

    def again(self):
        start = time.perf_counter()
        self.loader.flush()
        self.gen.render_pages(self.loader, self.out_dir)
        duration = time.perf_counter() - start
        print(f"Generated again in {duration:.2f}s.")

    def on_created(self, event):
        # for now we regenerate everything; this saves us having to work out dependencies.
        self.again()

    def on_modified(self, event):
        # for now we regenerate everything; this saves us having to work out dependencies.
        self.again()

    def on_deleted(self, event):
        # for now we regenerate everything; this saves us having to work out dependencies.
        self.again()


class TemplateFlushingEventHandler(FileSystemEventHandler):
    def __init__(self, gen: Gen, loader: Loader, out_dir: Path):
        self.loader = loader
        self.gen = gen
        self.out_dir = out_dir

    def again(self):
        start = time.perf_counter()
        self.gen.flush_tpls()
        self.gen.render_pages(self.loader, self.out_dir)
        duration = time.perf_counter() - start
        print(f"Reloaded templates and generated again in {duration:.2f}s.")

    def on_created(self, event):
        # for now we regenerate everything; this saves us having to work out dependencies.
        self.again()

    def on_modified(self, event):
        # for now we regenerate everything; this saves us having to work out dependencies.
        self.again()

    def on_deleted(self, event):
        # for now we regenerate everything; this saves us having to work out dependencies.
        self.again()


class CopyingEventHandler(FileSystemEventHandler):
    def __init__(self, static_dir: Path, out_dir: Path):
        self.static_dir = Path(static_dir).absolute()
        self.out_dir = out_dir

    def again(self, changed_file: Path | str):
        start = time.perf_counter()

        # We need to calculate the corresponding path in the out dir.
        changed_file = Path(changed_file).absolute()
        relative_path = changed_file.relative_to(self.static_dir)
        shutil.copy2(changed_file, self.out_dir / relative_path)

        duration = time.perf_counter() - start
        print(f"Updated {self.out_dir / relative_path} in {duration:.2f}s.")

    def on_created(self, event):
        # for now we regenerate everything; this saves us having to work out dependencies.
        self.again(event.src_path)

    def on_modified(self, event):
        # for now we regenerate everything; this saves us having to work out dependencies.
        self.again(event.src_path)


def main(argv: list[str] = None):
    arg_parser = ArgumentParser(description="Generate HTML from posts.")
    Config.add_arguments(arg_parser)
    arg_parser.add_argument(
        "--watch",
        "-w",
        action="store_true",
        help="Watch files & rerun when they change.",
    )
    arg_parser.add_argument(
        "--drafts",
        "-d",
        action="store_true",
        default=None,
        help="Include unpublished articles.",
    )
    arg_parser.add_argument(
        "--as-of",
        type=datetime.fromisoformat,
        default=None,
        help="Change the cut-off date for unpublished articles.",
    )
    args = arg_parser.parse_args(argv)
    config = Config.from_arguments(args)

    locale.setlocale(locale.LC_ALL, config.locale)

    now = args.as_of or datetime.now()
    include_drafts = args.drafts if args.drafts is not None else bool(args.watch)
    loader = Loader(config.pages_dirs, include_drafts=include_drafts, now=now)

    gen = Gen(
        config.templates_dir,
        config.static_dir,
        omit_dot_html=config.omit_dot_html,
    )
    gen.render_pages(loader, config.out_dir)

    if args.watch:
        print("Watching for changes ...")
        observer = Observer()
        posts_handler = GeneratingEventHandler(gen, loader, config.out_dir)
        for d in config.pages_dirs:
            observer.schedule(posts_handler, d, recursive=True)
        tpl_handler = TemplateFlushingEventHandler(gen, loader, config.out_dir)
        observer.schedule(tpl_handler, config.templates_dir, recursive=True)
        static_handler = CopyingEventHandler(config.static_dir, config.out_dir)
        observer.schedule(static_handler, config.static_dir, recursive=True)

        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


if __name__ == "__main__":
    sys.exit(main())
