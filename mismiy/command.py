from argparse import ArgumentParser
from datetime import datetime
import locale
from pathlib import Path
import shutil
import sys
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from mismiy.posts import Loader
from mismiy.gen import Gen


class GeneratingEventHandler(FileSystemEventHandler):
    def __init__(self, gen: Gen, loader: Loader, out_dir: Path):
        self.loader = loader
        self.gen = gen
        self.out_dir = out_dir

    def again(self):
        start = time.perf_counter()
        self.loader.flush()
        self.gen.render_posts(self.loader, self.out_dir)
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
        self.gen.render_posts(self.loader, self.out_dir)
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
    arg_parser.add_argument(
        "--templates-dir",
        "-t",
        metavar="PATH",
        default="templates",
        help="Directory containing mustache templates. Default is `templates`.",
    )
    arg_parser.add_argument(
        "--static-dir",
        "-s",
        metavar="PATH",
        default="static",
        help="Root of static files. Default is `static`.",
    )
    arg_parser.add_argument(
        "--out-dir",
        "-o",
        metavar="PATH",
        default="pub",
        help="Root of generated HTML tree. Default is `pub`.",
    )
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
    arg_parser.add_argument(
        "--locale",
        metavar="LOCALE",
        default="",
        help="Override the default locale. "
        "Must be a locale specifier like `en_GB.UTF-8`.",
    )
    arg_parser.add_argument(
        "posts_dir",
        metavar="PATH",
        nargs="?",
        default="posts",
        help="Directory with posts. Default is posts.",
    )
    args = arg_parser.parse_args(argv)

    locale.setlocale(locale.LC_ALL, args.locale or "")

    now = args.as_of or datetime.now()
    include_drafts = args.drafts if args.drafts is not None else bool(args.watch)
    loader = Loader(Path(args.posts_dir), include_drafts=include_drafts, now=now)

    gen = Gen(Path(args.templates_dir), Path(args.static_dir))
    gen.render_posts(loader, Path(args.out_dir))

    if args.watch:
        print("Watching for changes ...")
        observer = Observer()
        posts_handler = GeneratingEventHandler(gen, loader, Path(args.out_dir))
        observer.schedule(posts_handler, args.posts_dir, recursive=True)
        tpl_handler = TemplateFlushingEventHandler(gen, loader, Path(args.out_dir))
        observer.schedule(tpl_handler, args.templates_dir, recursive=True)
        static_handler = CopyingEventHandler(Path(args.static_dir), Path(args.out_dir))
        observer.schedule(static_handler, args.static_dir, recursive=True)

        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


if __name__ == "__main__":
    sys.exit(main())
