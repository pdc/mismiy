import contextlib
import locale
import shutil
import socket
import sys
import time
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import override

from strictyaml import Bool, Int, Map, Optional, Str, UniqueSeq
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
        Optional("port", default=8000): Int(),
        Optional("bind"): Str(),
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
    out_dir: Path = Path("pub")
    omit_dot_html: bool = False
    locale: str = ""
    port: int = 8001
    bind: str = ""

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
            omit_dot_html=(
                args.omit_dot_html
                if args.omit_dot_html is not None
                else defaults.get("omit_dot_html") or False
            ),
            locale=args.locale or defaults.get("locale") or "",
            port=defaults.get("port") or 8001,
            bind=defaults.get("bind") or "",
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
            help="Omit the .html suffix from href attributes.",
        )
        arg_parser.add_argument(
            "--bind",
            metavar="ADDRESS",
            help="When running dev server, bind to this address.",
        )
        arg_parser.add_argument(
            "--port",
            "-p",
            type=int,
            metavar="NUMBER",
            help="Override default port when running dev server.",
        )
        arg_parser.add_argument(
            "--locale",
            metavar="LOCALE",
            help="Override the default locale. Must be a locale specifier like `en_GB.UTF-8`.",
        )


class GeneratingEventHandler(FileSystemEventHandler):
    gen: Gen
    loader: Loader
    out_dir: Path

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
    gen: Gen
    loader: Loader
    out_dir: Path

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
    static_dir: Path
    out_dir: Path

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


class DirectorySettingHttpServer(ThreadingHTTPServer):
    """Web server serving files from a specified file-system directory."""

    dir_path: Path

    def __init__(self, dir_path: Path, server_address: tuple[str, int]):
        """Create a server, specifying the directory path."""
        self.dir_path = dir_path
        super().__init__(server_address, SimpleHTTPRequestHandler)

    # The following function is snarfed from standard library `http.server`.
    # It ensures the server listens to beoth IPv4 and IPv6 (when available) on
    # Microsoft Windows systems. Not tested by me.
    # https://github.com/python/cpython/issues/83088
    @override
    def server_bind(self):
        # Suppress exception when protocol is IPv4
        with contextlib.suppress(Exception):
            # The parameter 0 here means make the socket be NOT ipv6-only.
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        return super().server_bind()

    @override
    def finish_request(self, request, client_address):
        # This only works because self.RequestHandlerClass takes an extra parameter `directory`.
        self.RequestHandlerClass(request, client_address, self, directory=self.dir_path)  # pyright: ignore[reportCallIssue]


def main(argv: list[str] | None = None):
    """Parse the command-line arguments and do the thing."""
    arg_parser = ArgumentParser(description="Generate HTML from posts.")
    Config.add_arguments(arg_parser)
    arg_parser.add_argument(
        "--watch",
        "-w",
        action="store_true",
        help="Watch files & regenerate site when they change. Implies --drafts.",
    )
    arg_parser.add_argument(
        "--server",
        action="store_true",
        help="Be a development web server. Implies --watch, --drafts.",
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
    include_drafts = (
        args.drafts if args.drafts is not None else bool(args.watch or args.server)
    )
    loader = Loader(config.pages_dirs, include_drafts=include_drafts, now=now)

    gen = Gen(
        config.templates_dir,
        config.static_dir,
        omit_dot_html=config.omit_dot_html,
    )
    gen.render_pages(loader, config.out_dir)

    if args.watch or args.server:
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
            if args.server:
                host = config.bind or "localhost"
                host = f"[{host}]" if ":" in host else host
                print(f"Listening to http://{host}:{config.port} ...")
                addr = (config.bind, config.port)
                with DirectorySettingHttpServer(config.out_dir, addr) as httpd:
                    httpd.serve_forever()
            else:
                print("Watching for changes ...")
                while True:
                    time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


if __name__ == "__main__":
    sys.exit(main())
