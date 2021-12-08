icepyx
======

**Python tools for obtaining and working with ICESat-2 data**

|Documentation Status|  |GitHub license|  |Travis Dev Branch Build Status| |Code Coverage| |Conda install| |Pypi install|

.. |Documentation Status| image:: https://readthedocs.org/projects/icepyx/badge/?version=latest
   :target: http://icepyx.readthedocs.io/?badge=latest

.. |GitHub license| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
   :target: https://opensource.org/licenses/BSD-3-Clause

.. |Travis Dev Branch Build Status| image:: https://app.travis-ci.com/icesat2py/icepyx.svg?branch=development
    :target: https://app.travis-ci.com/icesat2py/icepyx

.. |Code Coverage| image:: https://codecov.io/gh/icesat2py/icepyx/branch/development/graph/badge.svg
    :target: https://codecov.io/gh/icesat2py/icepyx
    
.. |Conda install| image:: https://anaconda.org/conda-forge/icepyx/badges/installer/conda.svg 
    :target: https://anaconda.org/conda-forge/icepyx

.. |Pypi install| image:: https://badge.fury.io/py/icepyx.svg
    :target: https://pypi.org/project/icepyx/

Origin and Purpose
------------------
icepyx is both a software library and a community composed of ICESat-2 data users, developers, and the scientific community. We are working together to develop a shared library of resources - including existing resources, new code, tutorials, and use-cases/examples - that simplify the process of querying, obtaining, analyzing, and manipulating ICESat-2 datasets to enable scientific discovery.

icepyx aims to provide a clearinghouse for code, functionality to improve interoperability, documentation, examples, and educational resources that tackle disciplinary research questions while minimizing the amount of repeated effort across groups utilizing similar datasets. icepyx also hopes to foster collaboration, open-science, and reproducible workflows by integrating and sharing resources.

Many of these tools began as Jupyter Notebooks developed for and during the cryosphere themed ICESat-2 Hackweek
at the University of Washington in June 2019 or as scripts written and used by the ICESat-2 Science Team members.
This project combines and generalizes these scripts into a unified framework, making them accessible for everyone.


.. _`zipped file`: https://github.com/icesat2py/icepyx/archive/main.zip
.. _`Fiona`: https://pypi.org/project/Fiona/

Installation
------------

The simplest way to install icepyx is by using the
`conda <https://docs.conda.io/projects/conda/en/latest/user-guide/index.html>`__
package manager. |Conda install|
    
    conda install icepyx

Alternatively, you can also install icepyx using `pip <https://pip.pypa.io/en/stable/>`__. |Pypi install|

    pip install icepyx

More detailed instructions for installing `icepyx` can be found at
https://icepyx.readthedocs.io/en/latest/getting_started/install.html


Examples (Jupyter Notebooks)
----------------------------

Listed below are example jupyter-notebooks

`ICESat-2_DAAC_DataAccess_Example <https://github.com/icesat2py/icepyx/blob/main/examples/ICESat-2_DAAC_DataAccess_Example.ipynb>`_

`ICESat-2_DAAC_DataAccess2_Subsetting <https://github.com/icesat2py/icepyx/blob/main/examples/ICESat-2_DAAC_DataAccess2_Subsetting.ipynb>`_

`Working_with_ICESat-2_Data_Variables <https://github.com/icesat2py/icepyx/blob/main/examples/Working_with_ICESat-2_Data_Variables.ipynb>`_

`ICESat-2_Data_Visualization_Example <https://github.com/icesat2py/icepyx/blob/main/examples/ICESat-2_Data_Visualization_Example.ipynb>`_

`ICESat-2_Data_Read-in_Example <https://github.com/icesat2py/icepyx/blob/main/examples/ICESat-2_Data_Read-in_Example.ipynb>`_

`ICESat-2_cloud_data_access_example (BETA ONLY) <https://github.com/icesat2py/icepyx/blob/main/examples/ICESat-2_cloud_data_access_example.ipynb>`_

`ICESat-2_DEM_comparison_Colombia_working <https://github.com/icesat2py/icepyx/blob/main/examples/ICESat-2_DEM_comparison_Colombia_working.ipynb>`_

Citing icepyx
-------------
.. _`CITATION.rst`: ./CITATION.rst

This community and software is developed with the goal of supporting science applications. Thus, our contributors (including those who have developed the packages used within icepyx) and maintainers justify their efforts and demonstrate the impact of their work through citations. Please see  `CITATION.rst`_ for additional citation information.

Contact
-------
Working with ICESat-2 data and have ideas you want to share?
Have a great suggestion or recommendation of something you'd like to see
implemented and want to find out if others would like that tool too?
Come join the conversation at: https://discourse.pangeo.io/.
Search for "icesat-2" under the "science" topic to find us.

.. _`icepyx`: https://github.com/icesat2py/icepyx
.. _`contribution guidelines`: ./doc/source/contributing/contribution_guidelines.rst

Contribute
----------
We welcome and invite contributions to icepyx_ from anyone at any career stage and with any amount of coding experience!
Check out our `contribution guidelines`_ to see how you can contribute.

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms. |Contributor Covenant|

.. |Contributor Covenant| image:: https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg
   :target: code_of_conduct.md
   
Research notice
~~~~~~~~~~~~~~~

Please note that this repository is participating in a study into
sustainability of open source projects. Data will be gathered about this
repository for approximately the next 12 months, starting from June
2021.

Data collected will include number of contributors, number of PRs, time
taken to close/merge these PRs, and issues closed.

For more information, please visit `the informational
page <https://sustainable-open-science-and-software.github.io/>`__ or
download the `participant information
sheet <https://sustainable-open-science-and-software.github.io/assets/PIS_sustainable_software.pdf>`__.

