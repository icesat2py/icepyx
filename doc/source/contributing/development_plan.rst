icepyx Development Plan
=======================

This page provides a high-level overview of some focus areas of ongoing and for future icepyx development.
This list is not exclusive or highly specific.
Instead, specific development tasks and new functionality implementations are driven by individual developers/teams.

Our ongoing efforts are tracked as issues on our GitHub `issue tracker <https://github.com/icesat2py/icepyx/issues>`_.
We invite you to join the active discussions happening there.

Major Themes for Development
----------------------------

Enhancing User Interactivity and Visualization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
icepyx aims to continually reduce the need for researchers to rewrite "routine" code by enabling easy visualization
throughout the data inquiry to analyzed data presentation process and provide a simple, community-based framework for reproducibility.

Open Science Example Use Cases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Research is the primary driver for development of icepyx functionality.
If you are or plan to work on a project using ICESat-2 data, we encourage you to use icepyx as a framework for finding and processing your data, 
from designing your analysis to writing code to analyze your data to generating presentation-quality figures.
We welcome example use cases from all disciplines.

We would love for you to submit your example workflow showcasing your research.
Please :ref:`contact us<contact_ref_label>` if you have any questions or would like some guidance to get involved!

Data Analysis and Interaction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Many data analysis techniques (filtering, corrections, trend detection, feature detection, statistics, machine learning, etc.)
are used by researchers to analyze ICESat-2 data products.
As part of the broader Python ecosystem, relevant libraries that specialize in these techniques are easily incorporated into a single work environment.
In addition, creating ICESat-2 specific extensions for Xarray and Pandas data structures will enhance our ability to utilize these analysis tools
by providing easy ways to manipulate ICESat-2 data in the appropriate input type required by each library.
Workflows showcasing complex analyses to answer pressing science questions provide an opportunity for new reseachers to build on existing work.

Validation and Integration with Other Products
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The complexity of multiple data access systems, many with different metadata formats and API access types, 
presents a challenge for finding and integrating diverse datasets. 
Driven by researcher use cases, icepyx contains a framework for easily adding a new product/sensor to an existing data analysis pipeline,
improving researcher ability to easily compare diverse datasets across varying sensor types and spatial and temporal scales.

Modifying the Development Plan
------------------------------
Everyone is invited to review and propose new themes for the Development Plan.
icepyx is continually evolving and its direction is driven by your feedback and contributions.

If you'd like to add a theme to this development plan, please submit your idea as a GitHub issue to solicit community feedback.
Once there is agreement on your idea, submit a pull request to update the Development Plan, including a link to the discussion issue.