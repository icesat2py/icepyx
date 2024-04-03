.. _quest_supported_label:

QUEST Supported Datasets
========================

On this page, we outline the datasets that are supported by the QUEST module. Click on the links for each dataset to view information about the API and sensor/data platform used.


List of Datasets
----------------

`Argo <https://argo.ucsd.edu/data/>`_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The Argo mission involves a series of floats that are designed to capture vertical ocean profiles of temperature, salinity, and pressure down to ~2000 m. Some floats are in support of BGC-Argo, which also includes data relevant for biogeochemical applications: oxygen, nitrate, chlorophyll, backscatter, and solar irradiance.

For interested readers, a preprint outlining the QUEST module and its application to Argo data access is available `here <https://doi.org/10.22541/au.170258908.81399744/v1>`_.

`Argo Workflow Example <https://icepyx.readthedocs.io/en/latest/example_notebooks/QUEST_argo_data_access.html>`_

QUEST uses the Argovis API to access Argo data, so users are encouraged to use the following citation:

::

  Tucker, T., D. Giglio, M. Scanderbeg, and S.S.P. Shen, 2020. Argovis: A Web Applications for Fast Delivery, Visualization, and Analysis of Argo data. J. Atmos. Oceanic Technol., 37, 401-416, https://doi.org/10.1175/JTECH-D-19-0041.1

Citations for individual Argo datasets may be found at this link: https://argovis.colorado.edu/about


Adding a Dataset to QUEST
-------------------------

Want to add a new dataset to QUEST? No problem! QUEST includes a template script (``dataset.py``) that may be used to create your own querying module for a dataset of interest.

Once you have developed a script with the template, you may request for the module to be added to QUEST via GitHub.
Please see the How to Contribute page :ref:`dev_guide_label` for instructions on how to contribute to icepyx.

Detailed guidelines on how to construct your dataset module are currently a work in progress.
