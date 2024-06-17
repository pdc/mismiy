from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp


class TempDirMixin:
    """Create an empty test directory for each test.

    Directory and contents destroyed when test completes.
    """

    def setUp(self):
        super().setUp()
        self.test_dir = mkdtemp(prefix="TestPostsLoader")
        self.dir_path = Path(self.test_dir)

    def tearDown(self):
        rmtree(self.dir_path)
        super().tearDown()
