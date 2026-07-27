import os
import unittest
from argparse import ArgumentParser, Namespace
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

from mismiy import command

from .mixins import TempDirMixin


@contextmanager
def working_dir(dir_path: Path):
    prev_dir = os.getcwd()
    os.chdir(dir_path)
    yield
    os.chdir(prev_dir)


def no_args():
    arg_parser = ArgumentParser()
    command.Config.add_arguments(arg_parser)
    return arg_parser.parse_args([])


NO_ARGS = no_args()


class TestConfig(TempDirMixin, unittest.TestCase):
    def test_has_defaults_when_no_config(self):
        with working_dir(self.test_dir):
            config = command.Config.from_arguments(NO_ARGS)

        self.assertCountEqual(config.pages_dirs, [Path("posts")])
        self.assertEqual(config.static_dir, Path("static"))
        self.assertEqual(config.templates_dir, Path("templates"))
        self.assertEqual(config.out_dir, Path("pub"))
        self.assertEqual(config.omit_dot_html, False)
        self.assertEqual(config.locale, "")

    def test_reads_config_file(self):
        (self.dir_path / "mismiy-config.yaml").write_text(
            dedent("""
                pages_dirs:
                    - eggs
                    - bits
                templates_dir: tp
                static_dir: web
                out_dir: out
                omit_dot_html: true
                locale: en_DE.utf-16
                """)
        )

        with working_dir(self.dir_path):
            config = command.Config.from_arguments(NO_ARGS)

        self.assertCountEqual(config.pages_dirs, [Path("eggs"), Path("bits")])
        self.assertEqual(config.static_dir, Path("web"))
        self.assertEqual(config.templates_dir, Path("tp"))
        self.assertEqual(config.out_dir, Path("out"))
        self.assertEqual(config.omit_dot_html, True)
        self.assertEqual(config.locale, "en_DE.utf-16")

    def test_gives_precedence_to_args(self):
        (self.dir_path / "mismiy-config.yaml").write_text(
            dedent("""
                    pages_dirs:
                        - pages
                        - posts
                    templates_dir: tp
                    static_dir: web
                    out_dir: out
                    omit_dot_html: true
                    locale: en_DE.utf-16
                    """)
        )

        with working_dir(self.dir_path):
            os.chdir(self.dir_path)
            config = command.Config.from_arguments(
                Namespace(
                    pages_dirs=["socks", "shoes"],
                    templates_dir="partials",
                    static_dir="www",
                    out_dir="site",
                    omit_dot_html=False,
                    locale="cy_GB.utf-8",
                )
            )

        self.assertCountEqual(config.pages_dirs, [Path("socks"), Path("shoes")])
        self.assertEqual(config.static_dir, Path("www"))
        self.assertEqual(config.templates_dir, Path("partials"))
        self.assertEqual(config.out_dir, Path("site"))
        self.assertEqual(config.omit_dot_html, False)
        self.assertEqual(config.locale, "cy_GB.utf-8")


class TestCommand(TempDirMixin, unittest.TestCase):
    def test_uses_named_directories(self):
        with (
            working_dir(self.test_dir),
            patch.object(command, "Gen") as gen_cls,
            patch.object(command, "Loader") as loader_cls,
            patch.object(command, "datetime") as datetime_cls,
        ):
            datetime_cls.now.return_value = datetime(2024, 5, 20, 21, 7, 0)
            command.main(["-ss", "-oo", "-tt", "p"])

        loader_cls.assert_called_with(
            [Path("p")], include_drafts=False, now=datetime(2024, 5, 20, 21, 7, 0)
        )
        gen_cls.assert_called_with(Path("t"), Path("s"), omit_dot_html=False)
        gen_cls.return_value.render_pages.assert_called_with(
            loader_cls.return_value, Path("o")
        )

    def test_can_use_default_directories(self):
        with (
            working_dir(self.test_dir),
            patch.object(command, "Gen") as gen_cls,
            patch.object(command, "Loader") as loader_cls,
            patch.object(command, "datetime") as datetime_cls,
        ):
            datetime_cls.now.return_value = datetime(2024, 5, 20, 21, 7, 0)
            command.main([])

        loader_cls.assert_called_with(
            [Path("posts")], include_drafts=False, now=datetime(2024, 5, 20, 21, 7, 0)
        )
        gen_cls.assert_called_with(
            Path("templates"), Path("static"), omit_dot_html=False
        )
        gen_cls.return_value.render_pages.assert_called_with(
            loader_cls.return_value, Path("pub")
        )

    def test_can_override_drafts_inclusion(self):
        with (
            working_dir(self.test_dir),
            patch.object(command, "Gen"),
            patch.object(command, "Loader") as loader_cls,
            patch.object(command, "datetime", wraps=datetime) as datetime_cls,
        ):
            datetime_cls.now.return_value = datetime(2024, 5, 20, 21, 7, 0)
            command.main(["--drafts", "--as-of=2024-05-05"])

        loader_cls.assert_called_with(
            [Path("posts")], include_drafts=True, now=datetime(2024, 5, 5)
        )

    def test_can_omit_dot_html(self):
        # When called with --omit-dot-html …
        with (
            working_dir(self.test_dir),
            patch.object(command, "Gen") as gen_cls,
            patch.object(command, "Loader"),
        ):
            command.main(["--omit-dot-html"])

        # Then this is passed down to the generator.
        gen_cls.assert_called_with(
            Path("templates"), Path("static"), omit_dot_html=True
        )
