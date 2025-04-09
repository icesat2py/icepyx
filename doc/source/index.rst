.. |version badge| image:: https://badge.fury.io/gh/icesat2py%2Ficepyx.svg
    :target: https://badge.fury.io/gh/icesat2py%2Ficepyx

.. |JOSS| image:: https://joss.theoj.org/papers/10.21105/joss.04912/status.svg
    :alt: JOSS publication link and DOI
    :target: https://doi.org/10.21105/joss.04912

.. |Zenodo-all| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.7729175.svg
    :alt: Zenodo all-versions DOI for icepyx
    :target: https://doi.org/10.5281/zenodo.7729175


icepyx     |version badge|  |JOSS| |Zenodo-all|
===============================================

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
To further enhance data discovery, we have developed the QUEST module to facilitate querying of ICESat-2 data and complimentary Argo oceanographic data, with additional dataset support expected in the future.


.. grid:: 1 2 2 3
    :gutter: 3
    :class-container: sd-text-center

    .. grid-item-card::
        :img-top: https://cdn-icons-png.flaticon.com/128/2498/2498074.png
        :class-img-top: sd-p-2
        :class-card: sd-shadow-md

        **Getting Started**
        ^^^^^^^^^^^^^^^^^^^

        New to ICESat-2 or icepyx?
        Learn how to install icepyx and use it to jumpstart your project today.
        Check out our gallery of examples, too!

        .. button-ref:: install_ref
            :ref-type: ref
            :color: primary
            :outline:
            :expand:

            Installation Instructions

    .. grid-item-card::
        :img-top: https://cdn-icons-png.flaticon.com/128/3730/3730041.png
        :class-img-top: sd-p-2
        :class-card: sd-shadow-md

        **User Guide**
        ^^^^^^^^^^^^^^

        The user guide provides in-depth information on the tools and functionality
        available for obtaining and interacting with ICESat-2 data products.

        .. button-ref:: api_doc_ref
            :ref-type: ref
            :color: primary
            :outline:
            :expand:

            Software Docs

    .. grid-item-card::
        :img-top: https://cdn-icons-png.flaticon.com/256/9585/9585915.png
        :class-img-top: sd-p-2
        :class-card: sd-shadow-md

        **QUEST**
        ^^^^^^^^^

        Query, Unify, Explore SpatioTemporal (QUEST) is a module that extends icepyx functionality to other
        datasets.

        .. button-link:: https://icepyx.readthedocs.io/en/latest/example_notebooks/QUEST_argo_data_access.html
            :color: primary
            :outline:
            :expand:

            Start your QUEST!

    .. grid-item-card::
        :img-top: https://cdn-icons-png.flaticon.com/512/4230/4230997.png
        :class-img-top: sd-p-2
        :class-card: sd-shadow-md

        **Development Guide**
        ^^^^^^^^^^^^^^^^^^^^^

        Have an idea or an ancillary dataset to contribute to icepyx? Go here for information on best practices
        for developing and contributing to icepyx.

        .. button-ref:: dev_guide_label
            :ref-type: ref
            :color: primary
            :outline:
            :expand:

            Development Guide

    .. grid-item-card::
        :img-top: https://cdn-icons-png.flaticon.com/128/1283/1283342.png
        :class-img-top: sd-p-2
        :class-card: sd-shadow-md

        **Get in Touch**
        ^^^^^^^^^^^^^^^^

        icepyx is more than just software!
        We're a community of data producers, managers, and users
        who collaborate openly and share code and skills
        for every step along the entire data pipeline. Find resources for
        your questions here!

        .. button-ref:: contact_ref_label
            :ref-type: ref
            :color: primary
            :outline:
            :expand:

            Get Involved!

    .. grid-item-card::
        :img-top: https://icesat-2.gsfc.nasa.gov/sites/default/files/MissionLogo_0.png
        :class-img-top: sd-p-2
        :class-card: sd-shadow-md

        **ICESat-2 Resources**
        ^^^^^^^^^^^^^^^^^^^^^^

        Curious about other tools for working with ICESat-2 data?
        Want to share your resource?
        Check out the amazing work already in progress!

        .. button-ref:: resource_ref_label
            :ref-type: ref
            :color: primary
            :outline:
            :expand:

            ICESat-2 Resource Guide


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
   user_guide/documentation/icepyx-quest
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
