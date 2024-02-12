.. _quest_supported_label:

QUEST Supported Datasets
========================

On this page, we outline the datasets that are supported by the QUEST module. Click on the links for each dataset to view information about the API and sensor/data platform used.


List of Datasets
----------------

`Argo <https://argo.ucsd.edu/data/>`_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The Argo mission involves a series of floats that are designed to capture vertical ocean profiles of temperature, salinity, and pressure down to ~2000 m. Some floats are in support of BGC-Argo, which also includes data relevant for biogeochemical applications: oxygen, nitrate, chlorophyll, backscatter, and solar irradiance.

A paper outlining the Argo extension to QUEST is currently in preparation, with a citable preprint available in the near future.

`Argo Workflow Example <https://icepyx.readthedocs.io/en/latest/example_notebooks/QUEST_argo_data_access.html>`_


Adding a Dataset to QUEST
-------------------------

Want to add a new dataset to QUEST? No problem! QUEST includes a template script (``dataset.py``) that may be used to create your own querying module for a dataset of interest.

Once you have developed a script with the template, you may request for the module to be added to QUEST via GitHub.
Please see the How to Contribute page :ref:`dev_guide_label` for instructions on how to contribute to icepyx.

Detailed guidelines on how to construct your dataset module are currently a work in progress.
