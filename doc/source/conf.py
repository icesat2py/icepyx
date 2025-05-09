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
import datetime
import os
import sys

sys.path.insert(0, os.path.abspath("../.."))
sys.path.insert(0, os.path.abspath("../sphinxext"))

import icepyx

# -- Project information -----------------------------------------------------

project = "icepyx"
year = datetime.date.today().year
copyright = "2019-{}, The icepyx Development Team".format(year)

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    # IMPORTANT: napoleon must be loaded before sphinx_autodoc_typehints
    # https://github.com/tox-dev/sphinx-autodoc-typehints/issues/15
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "numpydoc",
    # "sphinx.ext.autosummary",
    "myst_nb",
    "contributors",  # custom extension, from pandas
    "sphinxcontrib.bibtex",
    "sphinx_design",
    # "sphinx.ext.imgconverter", # this extension should help the latex svg warning, but results in an error instead
]
myst_enable_extensions = [
    "linkify",
]

source_suffix = {
    # Note, put .rst first so that API docs are linked properly
    ".rst": "restructuredtext",
    ".ipynb": "myst-nb",
    ".txt": "myst-nb",
    ".md": "myst-nb",
}
# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "**.ipynb_checkpoints",
    "example_notebooks/supporting_files/*",
    "user_guide/changelog/template.rst",
]

# location of master document (by default sphinx looks for contents.rst)
master_doc = "index"

# bibtex file
bibtex_bibfiles = ["tracking/icepyx_pubs.bib"]

# -- Configuration options ---------------------------------------------------
# Prefix document path to section labels, to use:
# `path/to/file:heading` instead of just `heading`
autosectionlabel_prefix_document = True
autosummary_generate = True
numpydoc_show_class_members = False
nb_execution_mode = "off"
suppress_warnings = ["myst.header"]  # suppress non-consecutive header warning


# -- Options for Napoleon docstring parsing ----------------------------------
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True


# -- Options for autodoc -----------------------------------------------------

# Show the typehints in the description of each object instead of the signature.
autodoc_typehints = "description"


# -- Options for autodoc typehints--------------------------------------------

# Replace Union annotations with union operator "|"
always_use_bars_union = True
# always_document_param_types = True

# Show the default value for a parameter after its type
typehints_defaults = "comma"
typehints_use_return = True

# Options for intersphinx.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "logo_only": True,
    "display_version": False,
    "prev_next_buttons_location": "bottom",
    "navigation_depth": 4,
    "collapse_navigation": True,
}
html_logo = "_static/icepyx_v2_oval_orig_nobackgr.png"
html_favicon = "_static/icepyx_v2_oval_tiny-uml_nobackgr.png"
html_static_path = ["_static"]

html_context = {
    "menu_links_name": "",
    "menu_links": [
        (
            '<i class="fa fa-github fa-fw"></i> icepyx Github',
            "https://github.com/icesat2py/icepyx",
        ),
        (
            '<i class="fa fa-comments fa-fw"></i> Pangeo Discourse',
            "https://discourse.pangeo.io/t/icepyx-python-tools-for-icesat-2-data/404/2",
        ),
    ],
}


def setup(app):
    #     app.add_stylesheet("style.css")
    app.add_css_file("style.css")


# this should possibly be moved to the sphinxext directory as a standalone .py file
# -- custom style for pybtex output -------------------------------------------
# from pybtex.style.labels.alpha import LabelStyle as AlphaLabelStyle
from pybtex.plugin import register_plugin
from pybtex.style.formatting.unsrt import Style as UnsrtStyle

# I seem to be unable to figure out how to control what is used for the label. It would
# make sense if it were fed into this function, which then just formatted it, but I can't figure out from where
# class MyLabel(AlphaLabelStyle):
#     def format_label(self, entry):
# #         return entry.fields.get('comment')
#         return entry.key


class MyStyle(UnsrtStyle):
    name = "mystyle"
    default_name_style = "lastfirst"  # 'lastfirst' or 'plain'
    #     default_label_style = "mylabel"  # 'number' or 'alpha'
    default_sorting_style = "author_year_title"  # 'none' or 'author_year_title'

    def __init__(self, *args, **kwargs):
        super(MyStyle, self).__init__(*args, **kwargs)


#         self.label_style = MyLabel()
#         self.format_labels = self.label_style.format_label

# register_plugin("pybtex.style.labels", "mylabel", MyLabel)
register_plugin("pybtex.style.formatting", "mystyle", MyStyle)
