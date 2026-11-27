"""Sphinx configuration for the Project Icecrown documentation."""

from importlib.metadata import version as _version

project = "Project Icecrown"
author = "The Project Icecrown authors"
copyright = "the Project Icecrown authors, MIT licence"  # Sphinx's setting name
release = _version("icecrown")
version = release

extensions = [
    "myst_parser",
    "autoapi.extension",
    "sphinx.ext.napoleon",
]

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
exclude_patterns = ["_build"]
nitpicky = True

myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3

autoapi_type = "python"
autoapi_dirs = ["../src/icecrown"]
autoapi_root = "reference/api"
autoapi_options = ["members", "imported-members", "show-module-summary"]
autoapi_keep_files = False
autoapi_add_toctree_entry = False
autodoc_typehints = "description"

napoleon_google_docstring = True
napoleon_numpy_docstring = False

html_theme = "furo"
html_title = f"Project Icecrown {release}"
html_show_sourcelink = False
