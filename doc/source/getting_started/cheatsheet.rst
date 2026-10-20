.. _cheatsheet:

icepyx Cheatsheet
=================

A one-page reference for the most common icepyx tasks.
See the :doc:`example notebooks <../example_notebooks/IS2_data_access>` for full walkthroughs.

.. code-block:: python

    import icepyx as ipx


Log in to NASA Earthdata
------------------------

icepyx authenticates with `earthaccess <https://earthaccess.readthedocs.io/>`_
the first time a login is needed. Either set ``EARTHDATA_USERNAME`` and
``EARTHDATA_PASSWORD`` as environment variables, or enter your credentials
when prompted. A free account can be created at https://urs.earthdata.nasa.gov.


Define a query
--------------

.. code-block:: python

    # bounding box: [lower-left lon, lower-left lat, upper-right lon, upper-right lat]
    reg = ipx.Query("ATL06", [-55, 68, -48, 71], ["2019-02-20", "2019-02-28"])

    # polygon as a list of (lon, lat) vertices, or a path to a polygon file
    reg = ipx.Query("ATL06", [(-55, 68), (-55, 71), (-48, 71), (-48, 68), (-55, 68)],
                    ["2019-02-20", "2019-02-28"])
    reg = ipx.Query("ATL06", "/path/to/aoi.gpkg", ["2019-02-20", "2019-02-28"])

    # optional: version, orbital cycles and reference ground tracks
    reg = ipx.Query("ATL06", [-55, 68, -48, 71], cycles=["03", "04"], tracks=["0849"])


Explore the query
-----------------

.. code-block:: python

    reg.product, reg.product_version, reg.dates, reg.spatial_extent
    reg.product_summary_info()      # short product description
    reg.latest_version()            # most recent product version
    reg.visualize_spatial_extent()  # map of the area of interest


Find available granules
-----------------------

.. code-block:: python

    reg.avail_granules()                     # summary: count, size, dates
    reg.avail_granules(ids=True)             # granule IDs
    reg.avail_granules(cycles=True, tracks=True)
    reg.avail_granules(ids=True, cloud=True) # IDs and s3 urls for cloud access


Order and download
------------------

.. code-block:: python

    reg.show_custom_options()                # available subsetting options
    reg.order_granules()                     # spatially/temporally subset order
    reg.order_granules(subset=False)         # whole granules
    files = reg.download_granules("/path/to/data")


Read data into xarray
---------------------

.. code-block:: python

    reader = ipx.Read("/path/to/data/")          # a directory, a file, a glob or a list of files
    reader = ipx.Read("/path/to/**/folder", glob_kwargs={"recursive": True})

    reader.variables.avail()                     # variables in the files
    reader.variables.append(var_list=["h_li", "latitude", "longitude"])
    reader.variables.append(beam_list=["gt1l"], var_list=["h_li"])
    reader.variables.remove(all=True)            # start over

    ds = reader.load()                           # xarray.Dataset


Read directly from the cloud
----------------------------

.. code-block:: python

    ids, urls = reg.avail_granules(ids=True, cloud=True)
    reader = ipx.Read(urls[0])
    reader.variables.append(var_list=["h_li", "latitude", "longitude"])
    ds = reader.load()


Common ICESat-2 products
------------------------

========  =========================================================
ATL03     Global geolocated photon data
ATL06     Land ice height
ATL07     Sea ice height
ATL08     Land and vegetation height
ATL10     Sea ice freeboard
ATL11     Slope-corrected land ice height time series
ATL13     Inland water surface height
========  =========================================================
