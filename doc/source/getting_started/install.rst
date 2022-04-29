.. _`zipped file`: https://github.com/icesat2py/icepyx/archive/main.zip
.. _`Fiona`: https://pypi.org/project/Fiona/
.. |Conda install| image:: https://anaconda.org/conda-forge/icepyx/badges/installer/conda.svg 
    :target: https://anaconda.org/conda-forge/icepyx
    
.. |Pypi install| image:: https://badge.fury.io/py/icepyx.svg
    :target: https://pypi.org/project/icepyx/

.. _install_ref:

Installation
============

Quickstart
----------

The simplest way to install icepyx is by using the
`conda <https://docs.conda.io/projects/conda/en/latest/user-guide/index.html>`__
package manager. The command below takes care of setting up a virtual
environment and installs icepyx along with all the necessary dependencies::

    conda create --name icepyx-env --channel conda-forge icepyx

To activate the virtual environment, you can do::

    conda activate icepyx-env


Using conda |Conda install|
---------------------------

If you already have a virtual conda environment set up and activated, you can
install the latest stable release of icepyx from
`conda-forge <https://anaconda.org/conda-forge/icepyx>`__ like so::

    conda install icepyx

To upgrade an installed version of icepyx to the latest stable release, do::

    conda update icepyx



Using pip |Pypi install| 
------------------------

Alternatively, you can also install icepyx using `pip <https://pip.pypa.io/en/stable/>`__.

.. code-block::

  pip install icepyx


Windows users will need to first install `Fiona`_, please look at the instructions there.
Windows users may consider installing Fiona using pipwin

.. code-block::

  pip install pipwin
  pipwin install Fiona


Currently, conda and pip packages are generated with each tagged release.
This means it is possible that these methods will not install the latest merged features of icepyx.
In this case, icepyx is also available for use via the GitHub repository.
The contents of the repository can be downloaded as a `zipped file`_ or cloned.

To use icepyx this way, fork this repo to your own account, then git clone the repo onto your system.
To clone the repository:

.. code-block::

  git clone https://github.com/icesat2py/icepyx.git


Provided the location of the repo is part of your $PYTHONPATH, you should simply be able to add `import icepyx` to your Python document.
Alternatively, in a command line or terminal, navigate to the folder in your cloned repository containing setup.py and run

.. code-block::

  pip install -e.

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
