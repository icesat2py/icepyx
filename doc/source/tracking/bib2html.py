# modified from gimli-org/gimli: https://github.com/gimli-org/gimli/blob/4b646ff46e46ef71f1853ae5b060f98665dff9b6/doc/bib2html.py on 29 Oct 2020

import json

from bibtexparser import load
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode


def parse_bib(fname):
    """ Read bibtex file and sort by year. """

    with open(fname) as bibfile:
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        bp = load(bibfile, parser=parser)
        references = bp.get_entry_list()

    references.sort(key=lambda x: x["year"], reverse=True)

    return references


def write_html():
    db = parse_bib("icepyx_pubs.bib")
    for entry in db:
        entry["author"] = entry["author"].replace(" and ", ", ")
        entry["author"] = entry["author"].replace("~", " ")
        if not "journal" in entry:
            entry["journal"] = entry.pop("booktitle")
        entry["journal"] = "<i>%s</i>" % entry["journal"]
        if not "doi" in entry:
            string = ""
        else:
            doi = entry["doi"]
            link = "https://doi.org/%s" % doi
            string = (
                "<a target='_blank' href=%s data-toggle='tooltip' title='Go to %s'><i class='ai ai-doi ai-2x'></i></a>"
                % (link, link)
            )
        entry["doi"] = string

    return json.dumps(db, sort_keys=True, indent=4)
