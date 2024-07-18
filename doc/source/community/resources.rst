.. _resource_ref_label:

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
reproducible workflow that leverages existing tools wherever possible (see :ref:`Complementary GitHub Repositories <complementary_GH_repos_label>`)
and can be run locally, using high performance computing, or in the cloud.
A few other options available for querying, visualizing, and downloading ICESat-2 data files are:

- `earthaccess Python library <https://earthaccess.readthedocs.io>`_

  - A powerful tool for querying and downloading NASA datasets.
  - Seamlessly handles authentication and cloud tokening.
  - Under active development to expand functionality,
  including adding icepyx as a plugin to enable subsetting services for ICESat-2 data.

- `NSIDC (DAAC) Data Access <https://nsidc.org/data/icesat-2>`_

  - Select “Data from the right hand menu.
  Choose your dataset (ATL##).
  Then, use the spatial and temporal filters to narrow your list of granules available for download.

- `OpenAltimetry <https://openaltimetry.earthdatacloud.nasa.gov>`_

  - Collaboration between NSIDC, Scripps, and San Diego Supercomputer Center.
  - A web tool to visualize and download ICESat and ICESat-2 surface heights.
  - Data may be subsetted by data product, reference ground track (RGT), and beam.
  - Currently available ICESat-2 datasets are: ATL06 (land ice height), ATL07 (sea ice height),
  ATL08 (land/vegetation height), ATL10 (sea ice freeboard), ATL12 (ocean surface height), ATL13 (water surface height).

Software Packages for Working with ICESat-2 Data
------------------------------------------------
icepyx is but one of several software packages designed to improve user experience with ICESat-2 data.
The links below highlight other packages active in the community.

.. toctree::
  :maxdepth: 2

  resources/IS2_software

Resources Developed For and During Hackweeks
--------------------------------------------
Hackweeks give participants the opportunity to develop code to help download and/or analyze ICESat-2 data.
Many of these projects become inactive following the event, but they may provide useful workflows for users to work with.

.. toctree::
  :maxdepth: 2

  resources/2019_IS2_HW
  resources/2020_IS2_HW
  resources/2022_IS2_HW
  resources/2023_IS2_HW
