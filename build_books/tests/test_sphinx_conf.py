"""Unit tests for build_books/sphinx_conf.py configuration values.

sphinx_conf.py is a Sphinx configuration file that defines variables consumed
by the Sphinx build.  These tests validate that key configuration values are
set correctly and consistently.
"""

import os
import types

import pytest


@pytest.fixture(scope="module")
def conf():
    """Load sphinx_conf.py as a module."""
    src_path = os.path.join(
        os.path.dirname(__file__), os.pardir, "sphinx_conf.py"
    )
    src_path = os.path.abspath(src_path)
    mod = types.ModuleType("sphinx_conf")
    mod.__file__ = src_path
    # sphinx_conf.py is purely declarative (assignments, no side effects that
    # depend on the filesystem being a real Sphinx project), so we can exec it.
    with open(src_path, "r", encoding="utf-8") as f:
        code = f.read()
    exec(compile(code, src_path, "exec"), mod.__dict__)
    return mod


# ---------------------------------------------------------------------------
# Project metadata
# ---------------------------------------------------------------------------
class TestProjectMetadata:
    def test_project_name_is_set(self, conf):
        assert hasattr(conf, "project")
        assert isinstance(conf.project, str)
        assert len(conf.project) > 0

    def test_language_is_set(self, conf):
        assert conf.language == "cn"

    def test_master_doc(self, conf):
        assert conf.master_doc == "index"


# ---------------------------------------------------------------------------
# Extensions
# ---------------------------------------------------------------------------
class TestExtensions:
    def test_extensions_is_list(self, conf):
        assert isinstance(conf.extensions, list)

    def test_required_extensions_present(self, conf):
        required = [
            "myst_nb",
            "sphinx.ext.autodoc",
            "sphinx.ext.viewcode",
            "sphinx_copybutton",
        ]
        for ext in required:
            assert ext in conf.extensions, f"Missing extension: {ext}"


# ---------------------------------------------------------------------------
# HTML theme
# ---------------------------------------------------------------------------
class TestHtmlTheme:
    def test_theme_is_sphinx_book_theme(self, conf):
        assert conf.html_theme == "sphinx_book_theme"

    def test_html_title(self, conf):
        assert conf.html_title == "AI System"

    def test_static_path_exists(self, conf):
        assert isinstance(conf.html_static_path, list)
        assert "_static" in conf.html_static_path


# ---------------------------------------------------------------------------
# Theme options
# ---------------------------------------------------------------------------
class TestThemeOptions:
    def test_theme_options_is_dict(self, conf):
        assert isinstance(conf.html_theme_options, dict)

    def test_repository_url(self, conf):
        url = conf.html_theme_options.get("repository_url", "")
        assert "github.com" in url

    def test_icon_links_present(self, conf):
        links = conf.html_theme_options.get("icon_links", [])
        assert isinstance(links, list)
        assert len(links) >= 1
        names = [link["name"] for link in links]
        assert "GitHub" in names


# ---------------------------------------------------------------------------
# Exclude patterns
# ---------------------------------------------------------------------------
class TestExcludePatterns:
    def test_exclude_patterns_set(self, conf):
        assert isinstance(conf.exclude_patterns, list)
        assert "_build" in conf.exclude_patterns

    def test_ds_store_excluded(self, conf):
        assert ".DS_Store" in conf.exclude_patterns


# ---------------------------------------------------------------------------
# Myst extensions
# ---------------------------------------------------------------------------
class TestMystExtensions:
    def test_myst_enable_extensions_is_list(self, conf):
        assert isinstance(conf.myst_enable_extensions, list)

    def test_dollarmath_enabled(self, conf):
        assert "dollarmath" in conf.myst_enable_extensions
