"""Sphinx extension for using bibtex to format references - custom optinos
Ultimately pulled example from: https://stackoverflow.com/questions/55942749/how-do-you-change-the-style-of-pybtex-references-in-sphinx.

Usage::
    .. bibliography:: icepyx_pubs.bib
        :style: mystyle
        :all:

"""
from pybtex.style.formatting.unsrt import Style as UnsrtStyle
from pybtex.style.labels.alpha import LabelStyle as AlphaLabelStyle
from pybtex.plugin import register_plugin


class MyLabel(AlphaLabelStyle):
    def format_label(self, entry):
        return "APA"


class MyStyle(UnsrtStyle):
    name = "mystyle"
    default_name_style = "lastfirst"  # 'lastfirst' or 'plain'
    default_label_style = "mylabel"  # 'number' or 'alpha'
    default_sorting_style = "author_year_title"  # 'none' or 'author_year_title'

    def __init__(self, *args, **kwargs):
        super(MyStyle, self).__init__(*args, **kwargs)
        self.label_style = MyLabel()
        self.format_labels = self.label_style.format_label


# register_plugin('pybtex.style.labels', 'mylabel', MyLabel)
register_plugin("pybtex.style.formatting", "mystyle", MyStyle)
