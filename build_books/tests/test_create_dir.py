"""Unit tests for build_books/create_dir.py utility functions."""

import os
import shutil
import tempfile

import pytest

# The module has top-level code that runs on import (calls getallfile with
# hard-coded paths), so we import only the functions we need by loading the
# module source directly to avoid executing the script-level statements.
import importlib
import types


@pytest.fixture(scope="module")
def create_dir_mod():
    """Import create_dir.py as a module without executing top-level script code."""
    src_path = os.path.join(
        os.path.dirname(__file__), os.pardir, "create_dir.py"
    )
    src_path = os.path.abspath(src_path)
    with open(src_path, "r", encoding="utf-8") as f:
        source = f.read()

    # Remove everything after the function definitions (top-level script code)
    # by finding the first top-level assignment that is not inside a function.
    lines = source.splitlines(keepends=True)
    filtered = []
    for line in lines:
        # Stop at the hardcoded path assignments that begin the script section
        if line.startswith("target_dir") or line.startswith("dir_paths"):
            break
        if line.startswith("getallfile("):
            break
        filtered.append(line)

    mod = types.ModuleType("create_dir")
    mod.__file__ = src_path
    exec(compile("".join(filtered), src_path, "exec"), mod.__dict__)
    return mod


@pytest.fixture()
def tmp_dir(tmp_path):
    """Provide a temporary directory for tests."""
    return tmp_path


# ---------------------------------------------------------------------------
# del_dir_byname
# ---------------------------------------------------------------------------
class TestDelDirByname:
    def test_deletes_existing_directory(self, create_dir_mod, tmp_dir):
        target = tmp_dir / "to_delete"
        target.mkdir()
        assert target.exists()
        create_dir_mod.del_dir_byname(str(target))
        assert not target.exists()

    def test_nonexistent_directory_does_not_raise(self, create_dir_mod, tmp_dir):
        target = tmp_dir / "nonexistent"
        # Should print but not raise
        create_dir_mod.del_dir_byname(str(target))

    def test_deletes_nested_directory(self, create_dir_mod, tmp_dir):
        target = tmp_dir / "outer" / "inner"
        target.mkdir(parents=True)
        (target / "file.txt").write_text("data")
        create_dir_mod.del_dir_byname(str(tmp_dir / "outer"))
        assert not (tmp_dir / "outer").exists()


# ---------------------------------------------------------------------------
# create_dir
# ---------------------------------------------------------------------------
class TestCreateDir:
    def test_creates_new_directory(self, create_dir_mod, tmp_dir):
        result = create_dir_mod.create_dir(str(tmp_dir), "subdir")
        assert result is not None
        assert os.path.isdir(result)

    def test_returns_none_for_images_name(self, create_dir_mod, tmp_dir):
        result = create_dir_mod.create_dir(str(tmp_dir), "images")
        assert result is None

    def test_returns_none_for_name_containing_images(self, create_dir_mod, tmp_dir):
        result = create_dir_mod.create_dir(str(tmp_dir), "some_images_dir")
        assert result is None

    def test_recreates_existing_directory(self, create_dir_mod, tmp_dir):
        sub = tmp_dir / "existing"
        sub.mkdir()
        (sub / "old_file.txt").write_text("old")
        result = create_dir_mod.create_dir(str(tmp_dir), "existing")
        assert result is not None
        assert os.path.isdir(result)
        # Old contents should be gone because del_dir_byname was called first
        assert not (sub / "old_file.txt").exists()


# ---------------------------------------------------------------------------
# copystrtodir
# ---------------------------------------------------------------------------
class TestCopystrtodir:
    def test_copies_directory_tree(self, create_dir_mod, tmp_dir):
        src = tmp_dir / "source"
        src.mkdir()
        (src / "a.txt").write_text("hello")
        dest = tmp_dir / "dest"
        dest.mkdir()
        create_dir_mod.copystrtodir(str(src), str(dest), "copied")
        assert (tmp_dir / "dest" / "copied" / "a.txt").exists()
        assert (tmp_dir / "dest" / "copied" / "a.txt").read_text() == "hello"


# ---------------------------------------------------------------------------
# check_markdown
# ---------------------------------------------------------------------------
class TestCheckMarkdown:
    @pytest.mark.parametrize(
        "filename,expected",
        [
            ("README.md", True),
            ("notes.MD", False),  # case-sensitive
            ("file.txt", False),
            ("doc.pdf", False),
            ("page.md", True),
            ("noext", False),
            (".md", False),  # splitext(".md") -> (".md", "")
        ],
    )
    def test_check_markdown(self, create_dir_mod, filename, expected):
        assert create_dir_mod.check_markdown(filename) is expected


# ---------------------------------------------------------------------------
# check_pdf
# ---------------------------------------------------------------------------
class TestCheckPdf:
    @pytest.mark.parametrize(
        "filename,expected",
        [
            ("doc.pdf", True),
            ("doc.PDF", False),  # case-sensitive
            ("file.txt", False),
            ("README.md", False),
            (".pdf", False),  # splitext(".pdf") -> (".pdf", "")
        ],
    )
    def test_check_pdf(self, create_dir_mod, filename, expected):
        assert create_dir_mod.check_pdf(filename) is expected


# ---------------------------------------------------------------------------
# add2readme
# ---------------------------------------------------------------------------
class TestAdd2Readme:
    def test_appends_to_readme(self, create_dir_mod, tmp_dir):
        readme = tmp_dir / "README.md"
        readme.write_text("# Title\n", encoding="utf-8")
        create_dir_mod.add2readme(str(readme), "\nnew content")
        content = readme.read_text(encoding="utf-8")
        assert "new content" in content
        assert content.startswith("# Title\n")

    def test_ignores_non_readme(self, create_dir_mod, tmp_dir):
        other = tmp_dir / "NOTES.md"
        other.write_text("original", encoding="utf-8")
        create_dir_mod.add2readme(str(other), "should not appear")
        assert other.read_text(encoding="utf-8") == "original"


# ---------------------------------------------------------------------------
# change_iamgepath_markdown
# ---------------------------------------------------------------------------
class TestChangeImagepathMarkdown:
    def test_replaces_image_paths(self, create_dir_mod, tmp_dir):
        # Simulate a file at .../02Hardware02ChipBase/01CPUBase.md
        sub = tmp_dir / "02Hardware02ChipBase"
        sub.mkdir()
        md_file = sub / "01CPUBase.md"
        md_file.write_text(
            "![ENIAC01](images/01CPUBase01.png)\nSome text\n![other](images/other.png)",
            encoding="utf-8",
        )
        create_dir_mod.change_iamgepath_markdown(str(md_file))
        content = md_file.read_text(encoding="utf-8")
        expected_prefix = "../images/02Hardware02ChipBase/"
        assert expected_prefix + "01CPUBase01.png" in content
        assert expected_prefix + "other.png" in content
        # Original "images/" prefix should be gone
        assert "](images/" not in content

    def test_no_change_when_no_images_ref(self, create_dir_mod, tmp_dir):
        sub = tmp_dir / "section"
        sub.mkdir()
        md_file = sub / "plain.md"
        original = "No image references here."
        md_file.write_text(original, encoding="utf-8")
        create_dir_mod.change_iamgepath_markdown(str(md_file))
        assert md_file.read_text(encoding="utf-8") == original


# ---------------------------------------------------------------------------
# get_subfile (integration-style test)
# ---------------------------------------------------------------------------
class TestGetSubfile:
    def test_moves_md_files_and_returns_list(self, create_dir_mod, tmp_dir):
        # Source directory with markdown and images
        src = tmp_dir / "source_section"
        src.mkdir()
        (src / "README.md").write_text("# Readme\n", encoding="utf-8")
        (src / "01Intro.md").write_text("![img](images/pic.png)\n", encoding="utf-8")
        img_dir = src / "images"
        img_dir.mkdir()
        (img_dir / "pic.png").write_text("fake png", encoding="utf-8")

        # Destination directory
        dest = tmp_dir / "dest_section"
        dest.mkdir()

        # images target: derived from dir_path
        images_parent = tmp_dir / "images" / "dest_section"
        images_parent.mkdir(parents=True, exist_ok=True)

        result = create_dir_mod.get_subfile(str(src), str(dest))
        assert isinstance(result, list)
        assert len(result) == 2  # README.md + 01Intro.md
        # Markdown files should have been copied to dest
        assert (dest / "README.md").exists()
        assert (dest / "01Intro.md").exists()
