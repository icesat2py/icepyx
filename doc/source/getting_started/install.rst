


.. _`zipped file`: https://github.com/icesat2py/icepyx/archive/main.zip
.. _`Fiona`: https://pypi.org/project/Fiona/



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


Using conda 
-----------

If you already have a virtual conda environment set up and activated, you can
install the latest stable release of icepyx from
`conda-forge <https://anaconda.org/conda-forge/icepyx>`__ like so::

    conda install icepyx

To upgrade an installed version of icepyx to the latest stable release, do::

    conda update icepyx

Note: If this is you are doing a 'clean istall' of icepyx (i.e. without any of the required packages already installed in your local envrionment), you may encounter error messages when you try to import icepyx in your code. This is may be caused by the version of the rtree package according `this post <https://github.com/geopandas/geopandas/issues/1812>`__. When you use conda to install geopandas, it automatically installs all the dependencies, including rtree, with their newest version. To fix this issue, do::

    conda remove rtree
    conda install rtree=0.9.3
    conda install icepyx


Using pip 
---------

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
