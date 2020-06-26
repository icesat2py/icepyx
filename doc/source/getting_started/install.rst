


.. _`zipped file`: https://github.com/icesat2py/icepyx/archive/master.zip
.. _`Fiona`: https://pypi.org/project/Fiona/




Installation
============

The simplest way to install icepyx is using pip.

.. code-block::

  pip install icepyx


Windows users will need to first install `Fiona`_, please look at the instructions there. Windows users may consider installing Fiona using pipwin

.. code-block::

  pip install pipwin
  pipwin install Fiona 


Currently, packages are not automatically generated with each build, this means it is possible that pip will not install the latest release of icepyx. In this case, icepyx is also available for use via the GitHub repository. The contents of the repository can be download as a `zipped file`_ or cloned.

To use icepyx this way, fork this repo to your own account, then git clone the repo onto your system. 
To clone the repository:

.. code-block::

  git clone https://github.com/icesat2py/icepyx.git


Provided the location of the repo is part of your $PYTHONPATH, you should simply be able to add import icepyx to your Python document.
Alternatively, in a command line or terminal, navigate to the folder in your cloned repository containing setup.py and run

.. code-block::

  pip install -e


Future developments of icepyx may include conda as another simplified installation option.
