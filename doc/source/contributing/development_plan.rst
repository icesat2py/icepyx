icepyx Development Plan
=======================

This page provides a high-level overview of focus areas for icepyx's ongoing and future development.
This list is intentionally general and not exhaustive.
Instead, specific development tasks and new functionality implementations are driven by individual developers/teams.

Our ongoing efforts are tracked as issues on our GitHub `issue tracker <https://github.com/icesat2py/icepyx/issues>`_.
We invite you to join the active discussions happening there.

Major Themes for Development
----------------------------

Enhancing User Interactivity and Visualization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
icepyx aims to continually reduce the need for researchers to rewrite "routine" code by
enabling easy end-to-end data visualization and providing a simple, community-based framework for reproducibility.

Open Science Example Use Cases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Research is the primary driver for development of icepyx functionality.
We encourage you to use icepyx as a framework for finding and processing your ICESat-2 data,
from designing your analysis to writing code to analyze your data to generating presentation-quality figures.
We welcome example use cases from all disciplines.
Some topics currently being investigated using ICESat-2 data:
  - snow height in non-glaciated regions
  - subsurface ocean structure (including bathymetry)
  - vegetation canopy height
  - glacier ice velocity
  - sea level change
  - archaeological site discovery
  - phytoplankton concentrations under sea ice
  - iceberg detection

Please :ref:`contact us<contact_ref_label>`
if you have any questions or would like to submit an example workflow showcasing your research!

Data Analysis and Interaction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Many data analysis techniques (filtering, corrections, trend detection, feature detection, statistics, machine learning, etc.)
are used by researchers to analyze ICESat-2 data products.
As part of the broader Python ecosystem, relevant libraries that specialize in these techniques are easily incorporated into a single work environment.
In addition, creating ICESat-2 specific extensions for Xarray and Pandas data structures will enhance our ability to utilize these analysis tools
by providing easy ways to manipulate ICESat-2 data in the appropriate input type required by each library.
Workflows showcasing complex analyses to answer pressing science questions provide an opportunity for new reseachers to build on existing work.

Validation and Integration with Other Products
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The complexity of multiple data access systems, often with different metadata formats and API access types,
presents a challenge for finding and integrating diverse datasets.
Driven by researcher use cases, icepyx contains a consistent framework for adding a new product/sensor to an existing data analysis pipeline,
improving researcher ability to easily compare diverse datasets across varying sensor types and spatial and temporal scales.

Modifying the Development Plan
------------------------------
Everyone is invited to review and propose new themes for the Development Plan.
icepyx is continually evolving and its direction is driven by your feedback and contributions.

If you'd like to add a theme to this development plan,
please submit your idea in `GitHub Discussions <https://github.com/icesat2py/icepyx/discussions>`_ to solicit community feedback.
Once there is agreement on your idea, submit a pull request to update the Development Plan, including a link to the discussion.
