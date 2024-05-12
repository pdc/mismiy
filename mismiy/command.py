from argparse import ArgumentParser
from pathlib import Path
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


def main():
    arg_parser = ArgumentParser(description="Generate HTML from posts.")
    arg_parser.add_argument(
        "--partials-dir",
        "-p",
        metavar="PATH",
        default="partials",
        help="Root of mustache templates. Default is partials.",
    )
    arg_parser.add_argument(
        "--static-dir",
        "-s",
        metavar="PATH",
        default="static",
        help="Root of static files. Default is static.",
    )
    arg_parser.add_argument(
        "--out-dir",
        "-o",
        metavar="PATH",
        default="pub",
        help="Root of generated HTML tree. Default is pub.",
    )
    arg_parser.add_argument(
        "--watch",
        "-w",
        action="store_true",
        help="Watch files & rerun when they change.",
    )
    arg_parser.add_argument(
        "posts_dir",
        metavar="PATH",
        nargs="?",
        default="posts",
        help="Directory with posts. Default is posts.",
    )
    args = arg_parser.parse_args()

    loader = Loader(Path(args.posts_dir))
    gen = Gen(Path(args.partials_dir))
    gen.render_posts(loader, Path(args.out_dir))

    if args.watch:
        print("Watching for changes ...")
        observer = Observer()
        posts_handler = GeneratingEventHandler(gen, loader, Path(args.out_dir))
        observer.schedule(posts_handler, args.posts_dir, recursive=True)
        tpl_handler = TemplateFlushingEventHandler(gen, loader, Path(args.out_dir))
        observer.schedule(tpl_handler, args.partials_dir, recursive=True)

        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


if __name__ == "__main__":
    sys.exit(main())
