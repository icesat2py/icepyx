.. _resource_ref_label:
ICESat-2 Open-Source Resources Guide
====================================

This guide contains information regarding available resources for working with ICESat-2 datasets, both specifically (e.g. for ICESat-2 data) and more broadly (e.g. point cloud analysis of LiDAR datasets). It includes resources formally developed by/with support from NASA as well as individual and community efforts stemming from personal interest to ongoing research workflows.

Please feel free to add your project or another resource to this guide by submitting a pull request. We reserve the right to reject suggested resources that fall outside the scope of icepyx.

Resources Used in the Initial Development of icepyx
---------------------------------------------------

First ICESat-2 Cryospheric Hackweek at the University of Washington (June 2019)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This June 2019 event resulted in the production of a series of `tutorials <https://github.com/ICESAT-2HackWeek/ICESat2_hackweek_tutorials>`_, developed primarily by members of the ICESat-2 Science Team and early data users, aimed at educating the cryospheric community in obtaining and using ICESat-2 datasets. During the actual Hackweek, teams of researchers and data scientists developed a series of interesting `projects <https://github.com/ICESAT-2HackWeek/projects_2019>`_ related to their interests/research. 

The available tutorials, most of which contain one or more Jupyter Notebooks to illustrate concepts, are listed below. Additional information for citing (including licensing) and running (e.g. through a Pangeo Binder) these tutorials can be found at the above link.

1. `Overview of the ICESat-2 mission (slides) <https://github.com/ICESAT-2HackWeek/intro_ICESat2>`_
2. `Introduction to Open Science and Reproducible Research <https://github.com/ICESAT-2HackWeek/intro-jupyter-git>`_
3. `Access and Customize ICESat-2 Data via NSIDC API <https://github.com/ICESAT-2HackWeek/data-access>`_
4. `Intro to HDF5 and Reduction of ICESat-2 Data Files <https://github.com/ICESAT-2HackWeek/intro-hdf5>`_
5. `Clouds and ICESat-2 Data Filtering <https://github.com/ICESAT-2HackWeek/Clouds_and_data_filtering>`_
6. `Gridding and Filtering of ICESat/ICESat-2 Elevation Change Data <https://github.com/ICESAT-2HackWeek/gridding>`_
7. `ICESat-2 for Sea Ice <https://github.com/ICESAT-2HackWeek/sea-ice-tutorials>`_
8. `Geospatial Data Exploration, Analysis, and Visualization <https://github.com/ICESAT-2HackWeek/geospatial-analysis>`_
9. `Correcting ICESat-2 data and related applications <https://github.com/ICESAT-2HackWeek/data-correction>`_
10. `Numerical Modeling <https://gitlab.com/danshapero/icesat-2019-06-20>`_

Though in many cases preliminary, these `project repositories <https://github.com/ICESAT-2HackWeek/projects_2019>`_ can provide useful starting points to develop effective cryospheric workflows where more formal examples and functionality have not yet been developed.

*Sea Ice*

- `Floes are Swell <https://github.com/ICESAT-2HackWeek/Floes-are-Swell>`_

  - Calculate chord length (CLD) and lead width (LWD)

- `Segtrax <https://icesat2hackweek2019.slack.com/messages/CKQ08MBBR>`_

  - Create trajectories of sea ice motion (creates Python trajectory class)

*Glaciers and Ice Sheets*

- `Crackup <https://github.com/ICESAT-2HackWeek/crackup>`_

  - Investigating small-scale features such as crevasses and water depth

- `GlacierSat2 <https://github.com/ICESAT-2HackWeek/glaciersat2>`_

  - Constrain surface types (e.g. wet vs. dry snow) using ICESat-2 data over the Juneau Icefield, working towards looking at seasonal elevation changes

- `WaterNoice <https://github.com/ICESAT-2HackWeek/WaterNoice>`_

  - Detection of hydrologic features (e.g. meltwater ponds, firn aquifer seeps, blue ice megadunes, icebergs, etc.) in ATL06 land ice product

- `SnowBlower/blowing snow <https://github.com/ICESAT-2HackWeek/Snowblower>`_

  - Evaluate the blowing snow flag and look at blowing snow models

- `Cross-trak (xtrak) <https://github.com/ICESAT-2HackWeek/xtrak>`_

  - Interpolation between ICESat-2 tracks
  - Create gridded elevation data from multiple ICESat-2 tracks

- `Ground2Float <https://github.com/ICESAT-2HackWeek/ground2float>`_

  - Identify grounding zones using ICESat-2 data (using the slope-break method)

- `Topohack <https://github.com/ICESAT-2HackWeek/topohack>`_

  - Resolve topography over complex terrain

Complementary GitHub Repositories
---------------------------------
Here we describe a selection of publicly available Python code posted on GitHub with applicability for working with ICESat-2 data. This includes repositories that are more broadly designed for working with LiDAR/point cloud datasets in general. These repositories represent independent but complimentary projects that we hope to make easily interoperable within icepyx in order to maximize capabilities and minimize duplication of efforts. Conversations about how to best accomplish this have been ongoing since the conception of icepyx, and we welcome everyone to join the conversation (please see our :ref:`contact page<contact_ref_label>`).

*Note: This list is a compilation of publicly available GitHub repositories and includes some annotations to reflect how they relate to icepyx. Please check each repository's licensing information before using or modifying their code. Additional resources having to do specifically with obtaining ICESat-2 data are noted in the last section of this document.*

- `captoolkit <https://github.com/fspaolo/captoolkit>`_

  - by Fernando Paolo, Johan Nilsson, Alex Gardner
  - NASA's JPL Cryosphere Altimetry Processing Toolkit
  - Set of command line utilities to process, reduce, change format, etc. altimetry data from ICESat-2 and several other altimeters (e.g. ERS, CryoSat-2, IceBridge)
  - Includes utilities to read and extract variables of interest, compute and apply various corrections (e.g. tides, inverse barometer), detrend and correct data, do a variety of geographic computations and manipulations (e.g. raster math, masking, slope/aspect), and tile/grid/reduce data
  - We envision making captoolkit's utilities available as part of the icepyx ecosystem in order for users to quickly obtain and pre-process/correct/process ICESat-2 data.

- `Icesat2-viz <https://github.com/abarciauskas-bgse/icesat2-viz>`_

  - by Aimee Barciauskas-bgse
  - Exploration for visualizing ICESat-2 data products; focused on 3-D visualization using mapbox tools
  - We hope to take advantage of Icesat2-viz's work to provide 3-D visualizations of ICESat-2 data to expand on the 2-D visualization options currently available within icepyx.

- `Nsidc-subsetter <https://github.com/tsutterley/nsidc-subsetter>`_

  - by Tyler Sutterly
  - Retrieve IceBridge, ICESat, and ICESat-2 data using the NSIDC subsetter API
  - Command line tool
  - Download data and convert it into a georeferenced format (e.g. geojson, kml, or shapefile)
  - We envision use of Nsidc-subsetter to improve interoperability between icepyx and the NSIDC subsetter API. Currently, icepyx has very limited subsetting capabilities that are not easy to access or find more information about.

- `pointCollection <https://github.com/SmithB/pointCollection>`_

  - by Ben Smith
  - Efficiently organize and manipulate a database of points using this set of utilities
  - Access data fields using dot syntax and quickly index subsets of previously downloaded data
  - We hope to capitalize on some of the concepts of data access, indexing, and processing presented in pointCollection to improve our interfacing with ICESat-2 data within icepyx.


Other Ways to Access ICESat-2 Data
----------------------------------
icepyx aims to provide intuitive, object-based methods for finding, obtaining, visualizing, and analyzing ICESat-2 data as part of an open, reproducible workflow that leverages existing tools wherever possible (see `Complementary GitHub Repositories`_) and can be run locally, using high performance computing, or in the cloud using Pangeo. A few other options available for querying, visualizing, and downloading ICESat-2 data files are:

- `NSIDC (DAAC) Data Access <https://nsidc.org/data/icesat-2>`_

  - Select “ICESat-2 Data Sets” from the left hand menu. Choose your dataset (ATL##). Then, use the spatial and temporal filters to narrow your list of granules available for download.

- `OpenAltimetry <https://openaltimetry.org/>`_

  - Collaboration between NSIDC, Scripps, and San Diego Supercomputer Center
  - Enables data browsing on a map and selection of tracks and interactive data exploration for the higher level ICESat-2 datasets (i.e. ATL06+)
  

Ongoing Efforts
----------------
In addition to the ongoing development of icepyx itself, the ICESat-2 Cryosphere community continues to grow through a number of workshops and events.

Second [Virtual] ICESat-2 Cryospheric Hackweek Facilitated by the University of Washington
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
COVID-19 forced the in-person event to be cancelled, but we're excited to extend the Hackweek model into a virtual space, ultimately making it more accessible by removing the need to travel. This year's event is scheduled to take place from 15-18 June 2020, with multiple instructional sessions taking place during the preceding week (8-12 June) to limit the daily duration and accomodate multiple time zones. Though only selected participants are able to tune in to the live tutorial sessions, the materials being taught are freely available in the `ICESat-2 Hackweek GitHub Organization <https://github.com/ICESAT-2HackWeek>`_ respositories. Watch here for updates on projects conducted during the hackweek, and feel free to check out the event's `website <https://icesat-2hackweek.github.io/learning-resources/>`_.
