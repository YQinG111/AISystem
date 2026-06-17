"""Unit tests for build_books/watermark.py utility functions.

watermark.py has top-level code that opens a specific image file and iterates
over a directory, so we cannot import the module directly.  Instead we extract
the pure utility functions by compiling only the function definitions.
"""

import os
import shutil
import types

import pytest


@pytest.fixture(scope="module")
def watermark_mod():
    """Load only the function definitions from watermark.py."""
    src_path = os.path.join(
        os.path.dirname(__file__), os.pardir, "watermark.py"
    )
    src_path = os.path.abspath(src_path)
    with open(src_path, "r", encoding="utf-8") as f:
        source = f.read()

    # Keep only import statements and function defs; skip top-level
    # executable code (assignments that call Image.open, loops, etc.)
    lines = source.splitlines(keepends=True)
    filtered: list[str] = []
    inside_func = False
    for line in lines:
        stripped = line.strip()
        # Track whether we're inside a function body
        if stripped.startswith("def "):
            inside_func = True
            filtered.append(line)
            continue
        if inside_func:
            if line[0:1] in (" ", "\t") or stripped == "":
                filtered.append(line)
                continue
            else:
                inside_func = False
        # Keep import lines
        if stripped.startswith("import ") or stripped.startswith("from "):
            # Skip PIL import (not needed for the pure functions we test)
            if "PIL" in stripped:
                continue
            filtered.append(line)
            continue
        # Skip everything else (top-level assignments, loops, etc.)

    mod = types.ModuleType("watermark")
    mod.__file__ = src_path
    exec(compile("".join(filtered), src_path, "exec"), mod.__dict__)
    return mod


# ---------------------------------------------------------------------------
# check_image
# ---------------------------------------------------------------------------
class TestCheckImage:
    @pytest.mark.parametrize(
        "path,expected",
        [
            ("photo.png", True),
            ("photo.PNG", True),
            ("photo.jpg", True),
            ("photo.JPG", True),
            ("photo.jpeg", True),
            ("photo.JPEG", True),
            ("photo.bmp", True),
            ("photo.BMP", True),
            ("photo.tiff", True),
            ("photo.tif", True),
            ("photo.dib", True),
            ("photo.pbm", True),
            ("photo.pgm", True),
            ("photo.ppm", True),
            ("document.pdf", False),
            ("readme.md", False),
            ("script.py", False),
            ("noext", False),
            ("", False),
        ],
    )
    def test_image_detection(self, watermark_mod, path, expected):
        assert watermark_mod.check_image(path) is expected


# ---------------------------------------------------------------------------
# del_dir_byname
# ---------------------------------------------------------------------------
class TestDelDirByname:
    def test_deletes_existing_directory(self, watermark_mod, tmp_path):
        d = tmp_path / "removeme"
        d.mkdir()
        watermark_mod.del_dir_byname(str(d))
        assert not d.exists()

    def test_no_error_on_missing_directory(self, watermark_mod, tmp_path):
        watermark_mod.del_dir_byname(str(tmp_path / "nope"))


# ---------------------------------------------------------------------------
# create_dir
# ---------------------------------------------------------------------------
class TestCreateDir:
    def test_creates_directory(self, watermark_mod, tmp_path):
        target = tmp_path / "newdir"
        result = watermark_mod.create_dir(str(target))
        assert result == str(target)
        assert os.path.isdir(result)

    def test_recreates_existing_directory(self, watermark_mod, tmp_path):
        target = tmp_path / "existing"
        target.mkdir()
        (target / "file.txt").write_text("data")
        watermark_mod.create_dir(str(target))
        assert target.is_dir()
        # Old file should be gone
        assert not (target / "file.txt").exists()
