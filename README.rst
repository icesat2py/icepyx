icepyx
======

**Python tools for obtaining and working with ICESat-2 data**

|Documentation Status|
.. |Documentation Status| image:: https://readthedocs.org/projects/ansicolortags/badge/?version=latest
   :target: http://ansicolortags.readthedocs.io/?badge=latest

|GitHub license|
.. |GitHub license| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
   :target: https://opensource.org/licenses/BSD-3-Clause

Origin and Purpose
------------------
A library to simplify the process of downloading and manipulating ICESat-2 data to enable scientific discovery.
icepyx aims to provide a clearinghouse for code, documentation, examples,
and educational resources that tackle disciplinary research questions while minimizing
the amount of repeated effort across groups utilizing similar datasets.

Many of these tools began as Jupyter Notebooks developed for and during the cryosphere themed ICESat-2 Hackweek
at the University of Washington in June 2019 or as scripts written and used by the ICESat-2 Science Team members.
This project combines and generalizes these scripts into a unified framework, making them accessible for everyone.


.. _`zipped file`: https://github.com/icesat2py/icepyx/archive/master.zip

Installation
------------
Currently icepyx is only available for use as a github repository.
The contents of the repository can be download as a `zipped file`_ or cloned.

To use icepyx, fork this repo to your own account, then ``git clone`` the repo onto your system.
Provided the location of the repo is part of your $PYTHONPATH,
you should simply be able to add ``import icepyx`` to your Python document.

To clone the repository:

.. code-block:: none

  git clone git@github.com:icesat2py/icepyx.git


Future developments of icepyx may include pip and conda as simplified installation options.


Examples (Jupyter Notebooks)
----------------------------

.. _ICESat-2_DAAC_DataAccess_Example: ICESat-2_DAAC_DataAccess_Example.ipynb


Listed below are example jupyter-notebooks

ICESat-2_DAAC_DataAccess_Example_


Contact
-------
Working with ICESat-2 data and have ideas you want to share?
Have a great suggestion or recommendation of something you'd like to see
implemented and want to find out if others would like that tool too?
Come join the conversation at: https://discourse.pangeo.io/.
Search for "icesat-2" under the "science" topic to find us.

Contribute
----------
We welcome and invite contributions from anyone at any career stage and with any amount of coding experience!
To contribute to icepyx, simply fork this repo, make and commit your changes on your local branch,
and then submit a pull request with a clear message indicating what your changes accomplish.

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.
|Contributor Covenant|
.. |Contributor Covenant| image::https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg
   :target: code_of_conduct.md_