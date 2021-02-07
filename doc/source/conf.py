# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

import mone  # noqa: ignore=E402

# -- Project information -----------------------------------------------------

project = 'Mone'
copyright = '2020, Joe Pearson'
author = 'Joe Pearson'

# The full version, including alpha/beta/rc tags
version = mone.__version__
release = version

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx_copybutton',
    'sphinxcontrib.redoc',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# The document name of the 'master' document, that is, the document that
# contains the root toctree directive. Default is 'index'.
master_doc = 'index'

# Strip and configure input prompts for code cells
copybutton_prompt_text = ">>> "

# -- Options for autodoc -----------------------------------------------------

# This value selects if automatically documented members are sorted alphabetical
# (value 'alphabetical'), by member type (value 'groupwise') or by source order
# (value 'bysource').
autodoc_member_order = 'groupwise'

# This value contains a list of modules to be mocked up.
autodoc_mock_imports = []

# Both the class’ and the __init__ method’s docstring are concatenated and
# inserted.
autoclass_content = 'both'

# -- Options for autosummary -------------------------------------------------

autosummary_generate = True
autosummary_imported_members = False

# -- Options for intersphinx -------------------------------------------------

intersphinx_mapping = {
    'flask': ('https://flask.palletsprojects.com/', None),
    'python': ('https://docs.python.org/3', None)
}

# -- Options for ReDoc -------------------------------------------------------

redoc_uri = 'https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js'
redoc = [
    {
        'name': 'Bookkeeper API',
        'page': 'api',
        'spec': '../../mone/www/api/openapi.yaml',
        'embed': True,
    }
]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pydata_sphinx_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']
