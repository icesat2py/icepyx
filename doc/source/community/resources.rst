.. _resource_ref_label:

ICESat-2 Resource Guide
=======================

This guide contains information regarding available resources for working with ICESat-2 datasets, 
both specifically (e.g. for ICESat-2 data) and more broadly (e.g. point cloud analysis of LiDAR datasets). 
It includes resources formally developed by/with support from NASA as well as individual and 
community efforts stemming from personal interest to ongoing research workflows.

Please feel free to add your project or another resource to this guide by submitting a pull request. 
We reserve the right to reject suggested resources that fall outside the scope of icepyx.

Resources Developed For and During Hackweeks
--------------------------------------------

.. toctree::
  :titlesonly:

  resources/2019_IS2_HW
  resources/2020_IS2_HW
  IS2_software





Other Ways to Access ICESat-2 Data
----------------------------------
icepyx aims to provide intuitive, object-based methods for finding, obtaining, visualizing, and analyzing ICESat-2 data as part of an open, 
reproducible workflow that leverages existing tools wherever possible (see `Complementary GitHub Repositories`_) 
and can be run locally, using high performance computing, or in the cloud using Pangeo. 
A few other options available for querying, visualizing, and downloading ICESat-2 data files are:

- `NSIDC (DAAC) Data Access <https://nsidc.org/data/icesat-2>`_

  - Select “ICESat-2 Data Sets” from the left hand menu. Choose your dataset (ATL##). Then, use the spatial and temporal filters to narrow your list of granules available for download.

- `OpenAltimetry <https://openaltimetry.org/>`_

  - Collaboration between NSIDC, Scripps, and San Diego Supercomputer Center
  - Enables data browsing on a map and selection of tracks and interactive data exploration for the higher level ICESat-2 datasets (i.e. ATL06+)