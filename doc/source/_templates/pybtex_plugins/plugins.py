# from gimli-org/gimli/doc/_templates/pybtex_plugins/plugins.py: https://github.com/gimli-org/gimli/blob/2e358dc6f5cb62afd696e20457c00e7c164d39af/doc/_templates/pybtex_plugins/plugins.py on 29 Oct 2020

from pybtex.style.formatting.unsrt import Style as UnsrtStyle

# from pybtex.style.template import toplevel # ... and anything else needed


class MyStyle(UnsrtStyle):
    name = "mystyle"
    default_name_style = "lastfirst"  # 'lastfirst' or 'plain'
    default_label_style = "alpha"  # 'number' or 'alpha'
    default_sorting_style = "author_year_title"  # 'none' or 'author_year_title'

    # def format_XXX(self, e):
    # template = toplevel [
    ## etc.
    # ]
    # return template.format_data(e)


from pybtex.style.labels import BaseLabelStyle


class Alpha(BaseLabelStyle):
    name = "alpha"

    def format(self, entry):
        # print '#############################################'
        # print entry.__dict__
        return str(entry.key)
