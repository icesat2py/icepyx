Open-Source Packages
--------------------
ICESat-2 can be tricky to process for the first time, especially if working with the ATL03 data. Software packages have been developed to make ICESat-2 data analysis easier for new and experienced users.
Here, we highlight some commonly-used software packages developed by the science community. Most of these can be used alongside Icepyx to facilitate ICESat-2 data processing.
Most of these packages are callable through Python, though others may require access to other software. Keep this in mind before attempting to use any package or plugin.

* `SlideRule <https://github.com/ICESat2-SlideRule/sliderule-icesat2>`_

  - collaboration between the ICESat-2 science team and University of Washington
  - A Python client to process ICESat-2 ATL03 data prior to download.
  - Aggregates ATL03 data into line segments of user-defined length, creating a customized form of the ATL06 product.
  - Data may also be subsetted based on spatial bounds and photon classification.

* `IceFlow <https://github.com/nsidc/NSIDC-Data-Tutorials/tree/main/notebooks/iceflow>`_

  - by National Snow and Ice Data Center (NSIDC)
  - A Python library designed to simplify the co-registration of cryospheric datasets.
  - Matches georeferencing parameters across data sets, allowing a user to derive a time series across multiple datasets for a given region.
  - Currently valid datasets include ICESat, ICESat-2, and Operation IceBridge.

* `PhoREAL <https://github.com/icesat-2UT/PhoREAL>`_

  - by Applied Research Laboratories, University of Texas at Austin
  - A Python-based toolbox that may also be run as a GUI (Windows only).
  - Allows for quick processing of ATL03/08 data, which may then be used to generate 2-D plots of ICESat-2 surface heights.
  - Users may also convert processed data to .las, .csv, and .kml file formats.


.. _complementary_GH_repos_label:

Complementary GitHub Repositories
---------------------------------
Here we describe a selection of publicly available Python code posted on GitHub with applicability for working with ICESat-2 data.
This includes repositories that are more broadly designed for working with LiDAR/point cloud datasets in general.
These repositories represent independent but complimentary projects that we hope to make easily interoperable within icepyx in order to maximize capabilities and minimize duplication of efforts.
Conversations about how to best accomplish this have been ongoing since the conception of icepyx, and we welcome everyone to join the conversation (please see our :ref:`contact page<contact_ref_label>`).

*Note: This list is a compilation of publicly available GitHub repositories and includes some annotations to reflect how they relate to icepyx.
Please check each repository's licensing information before using or modifying their code.
Additional resources having to do specifically with obtaining ICESat-2 data are noted in the last section of this document.*

* `captoolkit <https://github.com/fspaolo/captoolkit>`_

  - by Fernando Paolo, Johan Nilsson, Alex Gardner
  - NASA's JPL Cryosphere Altimetry Processing Toolkit
  - Set of command line utilities to process, reduce, change format, etc. altimetry data from ICESat-2 and several other altimeters (e.g. ERS, CryoSat-2, IceBridge)
  - Includes utilities to read and extract variables of interest, compute and apply various corrections (e.g. tides, inverse barometer), detrend and correct data, do a variety of geographic computations and manipulations (e.g. raster math, masking, slope/aspect), and tile/grid/reduce data
  - We envision making captoolkit's utilities available as part of the icepyx ecosystem in order for users to quickly obtain and pre-process/correct/process ICESat-2 data.

* `Icesat2-viz <https://github.com/abarciauskas-bgse/icesat2-viz>`_

  - by Aimee Barciauskas-bgse
  - Exploration for visualizing ICESat-2 data products; focused on 3-D visualization using mapbox tools
  - We hope to take advantage of Icesat2-viz's work to provide 3-D visualizations of ICESat-2 data to expand on the 2-D visualization options currently available within icepyx.

* `Nsidc-subsetter <https://github.com/tsutterley/nsidc-subsetter>`_

  - by Tyler Sutterley
  - Retrieve IceBridge, ICESat, and ICESat-2 data using the NSIDC subsetter API
  - Command line tool
  - Download data and convert it into a georeferenced format (e.g. geojson, kml, or shapefile)
  - We envision use of Nsidc-subsetter to improve interoperability between icepyx and the NSIDC subsetter API. Currently, icepyx has very limited subsetting capabilities that are not easy to access or find more information about.

* `pointCollection <https://github.com/SmithB/pointCollection>`_

  - by Ben Smith
  - Efficiently organize and manipulate a database of points using this set of utilities
  - Access data fields using dot syntax and quickly index subsets of previously downloaded data
  - We hope to capitalize on some of the concepts of data access, indexing, and processing presented in pointCollection to improve our interfacing with ICESat-2 data within icepyx.


MATLAB Packages
---------------
* `PhotonLabeler <https://github.com/Oht0nger/PhoLabeler>`_

  - by Lonesome Malambo
  - A MATLAB-based user interface that allows for manual interpretation of ICESat-2 photons.
  - Users may classify photons based on surface type, signal/noise likelihood, or other user-defined labels.
  - Derives simple statistics for any user-defined photon classifications.
