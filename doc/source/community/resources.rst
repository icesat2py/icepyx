
ICESat-2 Resource Guide
=======================

This guide contains information regarding available resources for working with ICESat-2 datasets, 
both specifically (e.g. for ICESat-2 data) and more broadly (e.g. point cloud analysis of LiDAR datasets). 
It includes resources formally developed by/with support from NASA as well as individual and 
community efforts stemming from personal interest to ongoing research workflows.

Please feel free to add your project or another resource to this guide by submitting a pull request. 
We reserve the right to reject suggested resources that fall outside the scope of icepyx.

Other Ways to Access ICESat-2 Data
----------------------------------
icepyx aims to provide intuitive, object-based methods for finding, obtaining, visualizing, and analyzing ICESat-2 data as part of an open, 
reproducible workflow that leverages existing tools wherever possible (see :ref:`Complementary GitHub Repos<complementary_GH_repos_label>`) 
and can be run locally, using high performance computing, or in the cloud using Pangeo. 
A few other options available for querying, visualizing, and downloading ICESat-2 data files are:

- `NSIDC (DAAC) Data Access <https://nsidc.org/data/icesat-2>`_

  - Select “ICESat-2 Data Sets” from the left hand menu. Choose your dataset (ATL##). Then, use the spatial and temporal filters to narrow your list of granules available for download.

- `OpenAltimetry <https://openaltimetry.org/>`_

  - Collaboration between NSIDC, Scripps, and San Diego Supercomputer Center
  - A web tool to visualize and download ICESat and ICESat-2 surface heights
  - Data may be subsetted by data product, reference ground track (RGT), and beam
  - Currently available ICESat-2 datasets are: ATL06 (land ice height), ATL07 (sea ice height), ATL08 (land/vegetation height), ATL13 (water surface height)

Software Packages for Working with ICESat-2 Data
------------------------------------------------
icepyx is but one of several software packages designed to improve user experience with ICESat-2 data. The links below highlight other packages active in the community.

.. toctree::
  :maxdepth: 2

  resources/IS2_software

Resources Developed For and During Hackweeks
--------------------------------------------
Previous hackweeks gave participants the opportunity to develop codes to help download and/or analyze ICESat-2 data. Many of these projects are inactive, but they may provide useful workflows for users to work with.

.. toctree::
  :maxdepth: 2

  resources/2019_IS2_HW
  resources/2020_IS2_HW
  resources/2022_IS2_HW
