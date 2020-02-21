icepyx Development Plan
=======================

This page provides a high-level overview of where icepyx is headed. The list does not claim to be all inclusive, nor is it exclusive. Rather, we aim to provide a set of broad objectives to be met over the course of months to years, given that they require substantial developer time. These goals will evolve with time as development proceeds and new insights are gained (which could mean we ultimately opt NOT to implement some of them). If you would like to propose changes to this development plan, please see `Modifying the Development Plan`_

Items with a smaller scope are tracked as issues on our GitHub `issue tracker <https://github.com/icesat2py/icepyx/issues>`_. We invite you to join the active discussions happening there.

Enhancing User Interactivity and Visualization
----------------------------------------------
The process of querying, obtaining, and working with ICESat-2's large datasets through a command line or similar interface poses challenges to many researchers who are uninterested in also becoming advanced software developers. However, downloading, storing, and backing up both raw and derived data are computationally and resource intensive, and frequent switching between tools for different steps in the research workflow are time intensive and difficult to reproduce. By simplifying the process of querying, subsetting, and visualizing data - both through relevant function methods and interactive tools like Jupyter widgets - icepyx aims to reduce or remove the need to download large, non-subsetted datasets, enable easy visualization throughout the data inquiry to analyzed data presentation steps, and provide a simple, community-based framework for reproducibility.

Improving Accessibility to Advanced Computing
---------------------------------------------
Even as new resources and tools are developed to make computing easier, disciplinary researchers still face challenges finding time to maintain their computing environments while also meeting their research, teaching, and service objectives. Through integration of icepyx into the Pangeo ecosystem, only a handful of developers are able to manage the computational resources needed for working with ICESat-2 data, freeing researcher time and energy for exploring data. Further, the integration of Pangeo into existing advanced computing infrastructure (such as NASA's ADAPT) will enable researchers to take advantage of cloud computing without a significant need for re-tooling.

Open Science Example Use Cases
------------------------------
.. _`contact us`: ./contact.rst

We are currently partnering with multiple researchers conducting investigations using ICESat-2 datasets. Their research, from data collection and analysis to publication, will be used to drive the development of icepyx functionality, ultimately providing software contributions and example workflows. Current collaborations focus on:

- impacts of blowing snow and low clouds on ICESat-2 measurements
- snow height in non-glaciated regions
- parameter assimilation into sea ice models

If you are or plan to work on a project using ICESat-2 datasets, we encourage you to use icepyx as a framework for finding and processing your data, from designing your analysis to writing code to analyze your data (if the analysis tools you need aren't already a part of icepyx, that is!) to generating publication figures. Please `contact us`_ if you have any questions or would like some guidance to get involved!

Data Analysis and Interaction
-----------------------------
Multiple forms of traditional and advanced computational analysis are used by researchers to probe and analyze large datasets to answer challenging questions about the systems the data describes. These analysis techniques include filtering, application of corrections, trend detection, feature detection, statistics, and machine learning, among others. icepyx aims to easily integrate existing libraries that specialize in these types of analysis by providing easy ways to manipulate ICESat-2 data into the appropriate form required by each library and showcasing the use of these complex analyses to answer glaciological questions through easily-modifiable example workflows based on actual use cases.

Validation and Integration with Other Products
----------------------------------------------
The complexity of multiple data access systems, many with different metadata formats and API access types, presents a challenge for finding and integrating diverse datasets to construct long time series. Many open-source resources provide tools for manipulating certain types of datasets, but few collate these resources into one computing environment (see `Improve Accessibility of Advanced Computing`_) and provide wrappers and examples to easily conduct frequently performed analysis tasks. This portion of the development plan, driven by researcher use cases, will combine existing resources with new ones to improve researcher ability to easily compare diverse datasets across varying sensor types and spatial and temporal scales.

Modifying the Development Plan
------------------------------
Everyone is invited to review and propose new items for the Development Plan. icepyx is continually evolving and its direction is driven by your feedback and contributions.

Items listed in the Development Plan should be brief summaries of more detailed proposals. Each item listed should include:

1. Summary of proposed changes/additions
2. Motivation for the changes
3. Statement describing how the changes fit within the icepyx scope
4. More detailed plan for changes (e.g. implementation plan, examples (even if not implemented), potential issues)

Please submit your proposal as a GitHub issue, which will provide the developers and community members an opportunity to provide feedback on your suggestion. Once there is agreement on the proposal, submit a pull request to update the Development Plan, including a link to the discussion issue.