.. _dev_guide_label:

How to Contribute
=================

On this page we briefly provide basic instructions for contributing to icepyx.
We encourage users to follow the `git pull request workflow <https://www.asmeurer.com/git-workflow/>`_.
For contribution examples, please see contribution guidelines.


Contributing for the first time
-------------------------------
1. If you don't have one, sign up for a GitHub account (visit https://github.com/ and ‘sign up for GitHub account’).

2. Clone the icepyx repo: Open a terminal window.
Navigate to the folder on your computer where you want to store icepyx.
For example,

.. code-block:: shell

    cd /Users/YOURNAMEHERE/documents/ICESat-2

Within this folder, clone the icepyx repo by executing

.. code-block:: shell

    git clone https://github.com/icesat2py/icepyx.git

You should receive confirmation in terminal of the files loading into your workspace.
For help navigating git and GitHub, see this `guide <https://the-turing-way.netlify.app/collaboration/github-novice/github-novice-firststeps.html?highlight=github%20account>`__.
`GitHub <https://docs.github.com/en>`_ also provides a lot of great how-to materials for navigating and contributing.


Every time you contribute
-------------------------

1. To add new content, you need to create a new branch.
You can do this on GitHub by clicking the down arrow next to ‘development’ and making a new branch
(you can give it whatever name you want - the naming doesn't matter much as it will only be a temporary branch).

2. Navigate to the new branch you created.
Make any edits or additions on this branch (this can be done locally or on GitHub directly).
After you do this, commit your changes and add a descriptive commit message.

3. After committing the changes, push them to GitHub if you were working locally.
Then, open a pull request to merge your branch into the development branch.
Members of the icepyx community will review your changes and may ask you to make some more.

4. If this is your first PR, someone on the icepyx team should add you to the contributors list.
icepyx follows the `all-contributors <https://github.com/all-contributors/all-contributors>`_ specification using the contributors bot to add new contributors.
You are also welcome to add yourself by adding a comment with the text:

.. code-block:: none

    @all-contributors add @[GitHub_handle] for a, b, and c

where a, b, etc. is a list of the appropriate `contribution emojis <https://allcontributors.org/docs/en/emoji-key>`_.
The bot will open a separate PR to add the contributor or new contribution types!

5. Repeat these steps, creating a new branch and ultimately a pull request for each change.
More, smaller pull requests are easier to debug and merge than fewer large ones, so create pull requests regularly!


Steps for working with icepyx locally
-------------------------------------

Each time you begin working on icepyx (and especially each time you are about to create a new branch),
update your local copy of icepyx with

.. code-block:: shell

    git pull https://github.com/icesat2py/icepyx.git

to ensure you have the most up to date version of icepyx in your library.

Setting up a Development Work Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You will need to install icepyx in editable mode, so that when we make changes, they will immediately be testable at runtime.
You will also need icepyx's dependencies and some dev tooling (for automated checks, tests, and documentaiton).

To set this up, start in the root of your local copy of the icepyx repo.
Then, create a new environment using mamba (or conda, or a tool of your choice) and activate it.
Finally, install icepyx and needed dependencies in to it:

.. code-block:: shell

    mamba create --name icepyx-dev pip
    mamba activate icepyx-dev
    pip install --editable .[dev,docs]

Setting up development tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One of the dev tools we just installed is called `pre-commit <https://pre-commit.com/>`_.
We have included a set of pre-commit formatting hooks that we strongly encourage all contributors to use.
Configure those hooks to automatically execute with:

.. code-block:: shell

    pre-commit install

These hooks will check the files you are committing for format consistency and reformat them if necessary.
You can tell files were reformatted if you get a message showing one of the checks failed.
In this case, pre-commit has prevented the commit from completing.
You will need to re-add and the formatted files and try to commit again until all pre-commit hooks pass.

pre-commit will also run on icepyx PRs using the pre-commit CI (continuous integration) service.
As with other automations happening in PRs,
you'll want to make sure you pull the changes back to your local version before making new commits.


Considerations with Jupyter Notebook
------------------------------------

If you are working in Jupyter Notebook, in addition to manually installing your working version in your Python environment with

.. code-block:: shell

    pip install --editable .[dev,docs]

you will need to dynamically reload icepyx within your notebook by executing

.. code-block:: python

    %load_ext autoreload
    import icepyx as ipx
    %autoreload 2

in a notebook cell.
This allows the Jupyter Notebook to detect and use changes you've made to the underlying code.
