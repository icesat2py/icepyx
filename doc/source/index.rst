.. |version badge| image:: https://badge.fury.io/gh/icesat2py%2Ficepyx.svg
    :target: https://badge.fury.io/gh/icesat2py%2Ficepyx

.. |JOSS| image:: https://joss.theoj.org/papers/10.21105/joss.04912/status.svg
    :alt: JOSS publication link and DOI
    :target: https://doi.org/10.21105/joss.04912


icepyx     |version badge|  |JOSS|  
==========================

**Python tools for obtaining and working with ICESat-2 data**

Quick Links: 
:ref:`Installation<install_ref>` |
:ref:`Citation<citation>` |
`Examples <example_notebooks/IS2_data_access.html>`_ |
`Source Code <https://github.com/icesat2py/icepyx>`_ |
:ref:`Contact<contact_ref_label>`

icepyx is both a software library and a community composed of ICESat-2 data users, 
developers, and the scientific community. 
We are working together to develop a shared library of resources - 
including existing resources, new code, tutorials, and use-cases/examples - 
that simplify the process of querying, obtaining, analyzing, and manipulating 
ICESat-2 datasets to enable scientific discovery.


.. panels::
    :card: + intro-card text-center
    :column: col-lg-4 col-md-4 col-sm-6 col-xs-12 p-2
    :img-top-cls: pl-2 pr-2 pt-2 pb-2

    ---
    :img-top: https://cdn-icons-png.flaticon.com/128/2498/2498074.png

    **Getting Started**
    ^^^^^^^^^^^^^^^^^^^

    New to ICESat-2 or icepyx?
    Learn how to install icepyx and use it to jumpstart your project today.
    Check out our gallery of examples, too!

    .. link-button:: install_ref
        :type: ref
        :text: Installation Instructions
        :classes: stretched-link btn-outline-primary btn-block

    ---
    :img-top: https://cdn-icons-png.flaticon.com/128/3730/3730041.png

    **User Guide**
    ^^^^^^^^^^^^^^

    The user guide provides in-depth information on the tools and functionality
    available for obtaining and interacting with ICESat-2 data products.

    .. link-button:: api_doc_ref
        :type: ref
        :text: Software Docs
        :classes: stretched-link btn-outline-primary btn-block

    ---
    :img-top: https://cdn-icons-png.flaticon.com/256/9585/9585915.png

    **QUEST**
    ^^^^^^^^^^^^^^

    Query, Unify, Explore SpatioTemporal (QUEST) is a module that extends icepyx functionality to other 
    datasets. 

    .. link-button:: https://icepyx.readthedocs.io/en/latest/example_notebooks/QUEST_argo_data_access.html
        :type: ref
        :text: Start your QUEST!
        :classes: stretched-link btn-outline-primary btn-block

    ---
    :img-top: https://cdn-icons-png.flaticon.com/512/4230/4230997.png
    
    **Development Guide**
    ^^^^^^^^^^^^^^^^^^^^^

    Have an idea or an ancillary dataset to contribute to icepyx? Go here for information on best practices 
    for developing and contributing to icepyx.

    .. link-button:: dev_guide_label
        :type: ref
        :text: Development Guide
        :classes: stretched-link btn-outline-primary btn-block

    ---
    :img-top: https://cdn-icons-png.flaticon.com/128/1283/1283342.png

    **Get in Touch**
    ^^^^^^^^^^^^^^^^

    icepyx is more than just software!
    We're a community of data producers, managers, and users
    who collaborate openly and share code and skills
    for every step along the entire data pipeline. Find resources for
    your questions here!

    .. link-button:: contact_ref_label
        :type: ref
        :text: Get Involved!
        :classes: stretched-link btn-outline-primary btn-block

    ---
    :img-top: https://icesat-2.gsfc.nasa.gov/sites/default/files/MissionLogo_0.png
    :img-top-cls: pl-2 pr-2 pt-4 pb-4

    **ICESat-2 Resources**
    ^^^^^^^^^^^^^^^^^^^^^^

    Curious about other tools for working with ICESat-2 data?
    Want to share your resource?
    Check out the amazing work already in progress!

    .. link-button:: resource_ref_label
        :type: ref
        :text: ICESat-2 Resource Guide
        :classes: stretched-link btn-outline-primary btn-block


.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Getting Started

   getting_started/origin_purpose
   getting_started/install
   getting_started/citation_link

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Examples

   example_notebooks/IS2_data_access
   example_notebooks/IS2_data_access2-subsetting
   example_notebooks/IS2_data_variables
   example_notebooks/IS2_data_visualization
   example_notebooks/IS2_data_read-in
   example_notebooks/IS2_cloud_data_access
   example_notebooks/QUEST_argo_data_access

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: User Guide

   user_guide/documentation/icepyx
   user_guide/changelog/index

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Contributing

   contributing/contributors_link
   contributing/contribution_guidelines
   contributing/how_to_contribute
   contributing/attribution_link
   contributing/icepyx_internals
   contributing/quest-available-datasets
   contributing/development_plan
   contributing/release_guide
   contributing/code_of_conduct_link

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Community and Resources

   community/resources
   community/contact
   tracking/citations
   tracking/downloads

Icon images from `Flaticon <https://flaticon.com>`_ (by Freepik, Pixel perfect, and Eucalyp) 
and `NASA <https://www.nasa.gov/>`_.
