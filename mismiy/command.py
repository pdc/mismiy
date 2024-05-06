from argparse import ArgumentParser
from pathlib import Path
import sys

from mismiy.posts import Loader
from mismiy.gen import Gen


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
        "--out-dir",
        "-o",
        metavar="PATH",
        default="pub",
        help="Root of generated HTML tree. Default is pub.",
    )
    arg_parser.add_argument(
        "posts_dir",
        metavar="PATH",
        default="posts",
        help="Directory with posts. Default is posts.",
    )
    args = arg_parser.parse_args()

    loader = Loader(Path(args.posts_dir))
    gen = Gen(Path(args.partials_dir))
    gen.render_to(loader, Path(args.out_dir))


if __name__ == "__main__":
    sys.exit(main())
