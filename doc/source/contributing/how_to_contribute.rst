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


If you are modifying portions of code, you will need to run

.. code-block:: shell

    pip install -e.

within your Python environment to use your real-time edited version of the code during runtime.


Setting up a Development Work Environment
-----------------------------------------

icepyx uses a few tools to ensure that files have consistent formatting and run tests.
You can easily install the ones most frequently used by creating a new mamba (or conda)
environment (from the home level of your local copy of the icepyx repo) with

.. code-block:: shell

    mamba env create --name icepyx-env --channel conda-forge -f requirements-dev.txt -f requirements.txt

and then pip installing icepyx as described above and below.


Considerations with Jupyter Notebook
------------------------------------

If you are working in Jupyter Notebook, in addition to manually installing your working version in your Python environment with

.. code-block:: shell

    pip install -e.

you will need to dynamically reload icepyx within your notebook by executing

.. code-block:: python

    %load_ext autoreload
    import icepyx as ipx
    %autoreload 2

in a notebook cell.
This allows the Jupyter Notebook to detect and use changes you've made to the underlying code.
