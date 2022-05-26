How to contribute
=================

On this page we briefly provide basic instructions for contributing code to icepyx. 
For contribution examples, please see contribution guidelines.
In all cases, please follow the guidelines below. 

1. Sign up for a GitHub account

2. Clone the icepyx repo

3. Create a new temporary branch off development 

4. Add your name (in alphabetical order) to the contributors list

5. Submit a pull request of your temporary branch into development. You're officially part of our community!

6. For all future code contributions, create a new branch from the development branch and work from this branch. 

More details following each of these steps follow:

1. Sign up for your github account (visit https://github.com/ and  ‘sign up for GitHub account’)
2. For the purposes of adding your name to the contributors list, you need to create a new branch. You can do this by clicking the down arrow next to ‘development’ and making a new branch titled ‘new_contributor’ (or whatever you want to name it - the naming doesn't matter much as it will only be a temporary branch). 
3. Navigate to the new branch you created, click on CONTRIBUTORS.rst, and edit the document by adding your name in alphabetical order. After you do this, commit your changes and add a commit message ‘Added [your name here] to contributors list.’ 
4. After committing the changes, open a pull request to merge your branch into the development branch. Members of the icepyx community will review these changes.
5. After you’ve added yourself to the contributors list, clone the icepyx repo by navigating to `icepyx <https://github.com/icesat2py/icepyx>`__, clicking on the green ‘code’ button, copying the https link, then in your terminal where you want the folder, type:

        git clone https://github.com/icesat2py/icepyx.
Create a new branch within this cloned repo for the project you are working on. Work from this branch and regularly create pull requests to merge it with the development branch. 

For help navigating git and github, see this `guide <https://the-turing-way.netlify.app/collaboration/github-novice/github-novice-firststeps.html?highlight=github%20account>`__.

Considerations with Jupyter Notebook
------------------------------------

Note if you are working in jupyter notebook, you may need to dynamically reload icepyx using:
   
.. code-block::

    pip install -e.
    
    %load_ext autoreload
    import icepyx as ipx
    %autoreload 2
    
Steps for working with icepyx locally
-------------------------------------

On this page we briefly provide general steps for using icepyx. 

1. Sign up for a GitHub account: Sign up for your github account (visit https://github.com/ and  ‘sign up for GitHub account’)

2. Clone the icepyx repo: Open a terminal window. Navigate to the folder on your computer where you want to add icepyx code. For example, 

.. code-block::

    cd /Users/YOURNAMEHERE/documents/ICESat-2
    
Within this folder, clone the icepyx repo by writing 

.. code-block::

    git clone https://github.com/icesat2py/icepyx.git
    
You should receive confirmation in terminal of the files loading into your workspace. For help navigating git and github, see this `guide <https://the-turing-way.netlify.app/collaboration/github-novice/github-novice-firststeps.html?highlight=github%20account>`__.

For future sessions with icepyx, write 

.. code-block::

    git pull https://github.com/icesat2py/icepyx.git
    
to ensure you have the most up to date version of icepyx in your library. 


