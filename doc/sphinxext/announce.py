#!/usr/bin/env python3
"""
Script to generate contributor and pull request lists

This script generates contributor and pull request lists for release
announcements using Github v3 protocol. Use requires an authentication token in
order to have sufficient bandwidth, you can get one following the directions at
`<https://help.github.com/articles/creating-an-access-token-for-command-line-use/>_
Don't add any scope, as the default is read access to public information. The
token may be stored in an environment variable as you only get one chance to
see it.

Usage::

    $ ./scripts/announce.py <token> <revision range>

The output is utf8 rst.

Custom extension from the Pandas library:
https://github.com/pandas-dev/pandas/blob/1.1.x/doc/sphinxext/announce.py
Copied 10 August 2020 and subsequently modified.
Specifically, get_authors was adjusted to check for a .mailmap file
and use the git through the command line in order to utilize it if present.
Using a mailmap file is currently not possible in gitpython
(from git import Repo), and the recommended solution is to
bring in the mailmap file yourself and use it to modify the author list
(i.e. replicate the functionality that already exists in git).
This felt a bit out of time-scope for right now.
Alternatively, the git-fame library (imported as gitfame)
uses the mailmap file and compiles statistics,
but the python wrapper for this command line tool was taking forever.
So, I've reverted to using os.system to use git behind the scenes instead.

Dependencies
------------

- gitpython
- pygithub

Some code was copied from scipy `tools/gh_lists.py` and `tools/authors.py`.

Examples
--------

From the bash command line with $GITHUB token.

    $ ./scripts/announce.py $GITHUB v1.11.0..v1.11.1 > announce.rst

"""

import codecs
import os
import re
import textwrap

from git import Repo

UTF8Writer = codecs.getwriter("utf8")
this_repo = Repo(os.path.join(os.path.dirname(__file__), "..", ".."))

author_msg = """\
A total of %d people contributed to this release.  People with a
"+" by their names contributed for the first time.
"""

pull_request_msg = """\
A total of %d pull requests were merged for this release.
"""


def get_authors(revision_range):
    pat = "^.*\\t(.*)$"
    lst_release, cur_release = (r.strip() for r in revision_range.split(".."))

    if "|" in cur_release:
        # e.g. v1.0.1|HEAD
        maybe_tag, head = cur_release.split("|")
        assert head == "HEAD"
        if maybe_tag in this_repo.tags:
            cur_release = maybe_tag
        else:
            cur_release = head
        revision_range = f"{lst_release}..{cur_release}"

    # authors, in current release and previous to current release.
    # We need two passes over the log for cur and prev, one to get the
    # "Co-authored by" commits, which come from backports by the bot,
    # and one for regular commits.
    if ".mailmap" in os.listdir(this_repo.git.working_dir):
        xpr = re.compile(r"Co-authored-by: (?P<name>[^<]+) ")

        gitcur = list(os.popen("git shortlog -s " + revision_range).readlines())
        cur = []
        for n in gitcur:
            n = re.search(r".*?\t(.*)\n.*", n).group(1)
            cur.append(n)
        cur = set(cur)

        gitpre = list(os.popen("git shortlog -s " + lst_release).readlines())
        pre = []
        for n in gitpre:
            n = re.search(r".*?\t(.*)\n.*", n).group(1)
            pre.append(n)
        pre = set(pre)

    else:
        xpr = re.compile(r"Co-authored-by: (?P<name>[^<]+) ")
        cur = set(
            xpr.findall(
                this_repo.git.log("--grep=Co-authored", "--pretty=%b", revision_range)
            )
        )
        cur |= set(re.findall(pat, this_repo.git.shortlog("-se", revision_range), re.M))

        pre = set(
            xpr.findall(
                this_repo.git.log("--grep=Co-authored", "--pretty=%b", lst_release)
            )
        )
        pre |= set(re.findall(pat, this_repo.git.shortlog("-se", lst_release), re.M))

        # Homu is the author of auto merges, clean him out.
    #     cur.discard("Homu")
    #     pre.discard("Homu")

    # Append '+' to new authors.
    authors = [s + " +" for s in cur - pre] + [s for s in cur & pre]
    authors.sort()
    return authors


def get_pull_requests(repo, revision_range):
    prnums = []

    # From regular merges
    merges = this_repo.git.log("--oneline", "--merges", revision_range)
    issues = re.findall("Merge pull request \\#(\\d*)", merges)
    prnums.extend(int(s) for s in issues)

    # From Homu merges (Auto merges)
    issues = re.findall("Auto merge of \\#(\\d*)", merges)
    prnums.extend(int(s) for s in issues)

    # From fast forward squash-merges
    commits = this_repo.git.log(
        "--oneline", "--no-merges", "--first-parent", revision_range
    )
    issues = re.findall("^.*\\(\\#(\\d+)\\)$", commits, re.M)
    prnums.extend(int(s) for s in issues)

    # get PR data from github repo
    prnums.sort()
    prs = [repo.get_pull(n) for n in prnums]
    return prs


def build_components(revision_range, heading="Contributors"):
    lst_release, cur_release = (r.strip() for r in revision_range.split(".."))
    authors = get_authors(revision_range)

    return {
        "heading": heading,
        "author_message": author_msg % len(authors),
        "authors": authors,
    }


def build_string(revision_range, heading="Contributors"):
    components = build_components(revision_range, heading=heading)
    components["uline"] = "=" * len(components["heading"])
    components["authors"] = "* " + "\n* ".join(components["authors"])

    # Don't change this to an fstring. It breaks the formatting.
    tpl = textwrap.dedent(
        """\
    {heading}
    {uline}

    {author_message}
    {authors}"""
    ).format(**components)
    return tpl


def main(revision_range):
    # document authors
    text = build_string(revision_range)
    print(text)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Generate author lists for release")
    parser.add_argument("revision_range", help="<revision>..<revision>")
    args = parser.parse_args()
    main(args.revision_range)


"""
Early attempts at implementing use of mailmap within this script:

cur = re.compile('|'.join(map(re.escape, ['<*>'])))
# ------------
with open(os.path.join(os.path.dirname('[fill in here]'), "[repo_name]/.mailmap")) as f:
    l = [line.rstrip('\n') for line in f]

m={}
for line in l:
    try:
        m.update(dict(line.split('> ')))
    except ValueError:
        m.update({line:''})
"""
