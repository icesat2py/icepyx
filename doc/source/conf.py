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
import contextlib
import os
import sys
from pkg_resources import DistributionNotFound, get_distribution

sys.path.insert(0, os.path.abspath("../.."))
sys.path.insert(0, os.path.abspath("../sphinxext"))
import datetime

import icepyx
import recommonmark


# -- Project information -----------------------------------------------------

project = "icepyx"
year = datetime.date.today().year
copyright = "2019-{}, The icepyx Developers".format(year)

# -- General configuration ---------------------------------------------------

@contextlib.contextmanager
def chdir(directory):
    curdir = os.curdir
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(curdir)


try:
    dist = get_distribution(project)
except DistributionNotFound:
    # The project is not installed in readthedocs environment (requires LDAP
    # bindings). Read the version with setuptools_scm.
    import setuptools_scm

    with chdir("../.."):
        release = setuptools_scm.get_version()
else:
    release = dist.version
version = ".".join(release.split(".")[:2])

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "numpydoc",
    "nbsphinx",
    "recommonmark",
    "contributors",  # custom extension, from pandas
    "sphinxcontrib.bibtex",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}
# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["**.ipynb_checkpoints"]

# location of master document (by default sphinx looks for contents.rst)
master_doc = "index"

# bibtex file
bibtex_bibfiles = ["tracking/icepyx_pubs.bib"]

# -- Configuration options ---------------------------------------------------
autosummary_generate = True
numpydoc_show_class_members = False


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "logo_only": True,
    "display_version": False,
    "prev_next_buttons_location": None,
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
from pybtex.style.formatting.unsrt import Style as UnsrtStyle
from pybtex.style.labels.alpha import LabelStyle as AlphaLabelStyle
from pybtex.plugin import register_plugin

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
