import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from mismiy import command

from .mixins import TempDirMixin


class TestCommand(TempDirMixin, unittest.TestCase):
    def test_uses_named_directories(self):
        with patch.object(command, "Gen") as gen_cls, patch.object(
            command, "Loader"
        ) as loader_cls, patch.object(command, "datetime") as datetime_cls:
            datetime_cls.now.return_value = datetime(2024, 5, 20, 21, 7, 0)
            command.main(["-ss", "-oo", "-tt", "p"])

        loader_cls.assert_called_with(
            [Path("p")], include_drafts=False, now=datetime(2024, 5, 20, 21, 7, 0)
        )
        gen_cls.assert_called_with(Path("t"), Path("s"))
        gen_cls.return_value.render_pages.assert_called_with(
            loader_cls.return_value, Path("o")
        )

    def test_can_use_default_directories(self):
        with patch.object(command, "Gen") as gen_cls, patch.object(
            command, "Loader"
        ) as loader_cls, patch.object(command, "datetime") as datetime_cls:
            datetime_cls.now.return_value = datetime(2024, 5, 20, 21, 7, 0)
            command.main([])

        loader_cls.assert_called_with(
            [Path("posts")], include_drafts=False, now=datetime(2024, 5, 20, 21, 7, 0)
        )
        gen_cls.assert_called_with(Path("templates"), Path("static"))
        gen_cls.return_value.render_pages.assert_called_with(
            loader_cls.return_value, Path("pub")
        )

    def test_can_override_drafts_inclusion(self):
        with patch.object(command, "Gen"), patch.object(
            command, "Loader"
        ) as loader_cls, patch.object(
            command, "datetime", wraps=datetime
        ) as datetime_cls:
            datetime_cls.now.return_value = datetime(2024, 5, 20, 21, 7, 0)
            command.main(["--drafts", "--as-of=2024-05-05"])

        loader_cls.assert_called_with(
            [Path("posts")], include_drafts=True, now=datetime(2024, 5, 5)
        )
