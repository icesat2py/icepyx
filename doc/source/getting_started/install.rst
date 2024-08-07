.. _`zipped file`: https://github.com/icesat2py/icepyx/archive/main.zip
.. _`Fiona`: https://pypi.org/project/Fiona/
.. |Conda install| image:: https://anaconda.org/conda-forge/icepyx/badges/version.svg
    :target: https://anaconda.org/conda-forge/icepyx

.. |Pypi install| image:: https://badge.fury.io/py/icepyx.svg
    :target: https://pypi.org/project/icepyx/

.. _install_ref:

Installation
============

Quickstart
----------

The simplest (and recommended) way to install icepyx is by using the
`mamba <https://mamba.readthedocs.io/en/latest/index.html>`_ package
manager (or `conda <https://docs.conda.io/projects/conda/en/latest/user-guide/index.html>`_,
which can be used in place of any of the mamba commands shown here).
The command below takes care of setting up a virtual
environment and installs icepyx along with all the necessary dependencies::

    mamba env create --name icepyx-env --channel conda-forge icepyx

To activate the virtual environment, you can do::

    mamba activate icepyx-env


Using mamba |Conda install|
---------------------------

If you already have a virtual mamba/conda environment set up and activated, you can
install the latest stable release of icepyx from
`conda-forge <https://anaconda.org/conda-forge/icepyx>`__ like so::

    mamba install icepyx

To upgrade an installed version of icepyx to the latest stable release, do::

    mamba update icepyx



Using pip |Pypi install|
------------------------

Alternatively, you can also install icepyx using `pip <https://pip.pypa.io/en/stable/>`__.

.. code-block::

  pip install icepyx


Windows users will need to first install `Fiona`_; please look at the instructions there.
Windows users may consider installing Fiona using pipwin

.. code-block::

  pip install pipwin
  pipwin install Fiona


For the latest features
-----------------------

Currently, conda-forge and pip packages are generated with each tagged release.
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
