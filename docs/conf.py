""" sphinx docs configuration """

# Must be disabled for copyright variable
# pylint: disable=invalid-name

import os
from datetime import datetime
import sys

import sphinx_rtd_theme

# https://github.com/sphinx-doc/sphinx/issues/4317
sys.path.insert(0, os.path.abspath("../"))



project = "keggtools"
author = "harryhaller001"
copyright = f'{datetime.now():%Y}, {author}.' # pylint: disable=redefined-builtin
version = "0.5.0"
release = version

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    # "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
]

# Mapping for intersphinx extension
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pandas': ('http://pandas.pydata.org/pandas-docs/dev', None),
}


source_suffix = '.rst'
master_doc = "index"
pygments_style = 'sphinx'


exclude_trees = [
    "_build",
    "cloudflare-workers",
    "dist"
]

exclude_patterns = [
    "wrangler.toml",
    "wrangler.toml.example",
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

# Generate the API documentation when building
autosummary_generate = True
autodoc_member_order = "bysource"
autoapi_dirs = ["../keggtools"]

# Configuration of sphinx.ext.coverage
coverage_show_missing_items = True


# Configurate sphinx rtd theme
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_show_sphinx = False
html_context = dict(
    display_github=True,
    github_user='harryhaller001',
    github_repo='keggtools',
    github_version='main',
    conf_py_path='/docs/',
)


html_static_path = ['static']

# Addind custom css script
html_css_files = [
    'css/custom.css',
]
