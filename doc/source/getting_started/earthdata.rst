=====
NSIDC
=====

NASA has 12 `Distributed Active Archive Centers (DAACs) <https://earthdata.nasa.gov/about/daacs>`_
throughout the United States.
All ICESat-2 data is archived and stored at the NASA DAAC at the
`National Snow and Ice Data Center (NSIDC) <https://nsidc.org/daac/>`_.
``icepyx`` uses `NASA Common Metadata Repository (CMR) <https://cmr.earthdata.nasa.gov/search>`_
queries to search for ICESat-2 granules that fit a given set of spatial, temporal or orbital parameters.
These granules can then be requested and downloaded from the NSIDC archives.
Granules returned by the CMR system may occasionally not spatially intersect the region of interest.
This is due to a spatial margin (buffer) applied to the ICESat-2 CMR resources.

Startup Steps for NSIDC
#######################

1. `Register with NASA Earthdata Login system <https://urs.earthdata.nasa.gov/users/new>`_
2. Use your NASA Earthdata credentials either:

   * Directly in an ``icepyx`` Notebook
   * Permanently with a `.netrc file <https://nsidc.org/support/how/v0-programmatic-data-access-guide>`_

    .. code-block:: bash

        echo "machine urs.earthdata.nasa.gov login <uid> password <password>" >> ~/.netrc
        chmod 0600 ~/.netrc

   * Temporarily with an environmental variable before running ``icepyx``

    .. code-block:: bash

        export EARTHDATA_PASSWORD=<password>

Other Data Access Examples
##########################

- `Curl and Wget <https://wiki.earthdata.nasa.gov/display/EL/How+To+Access+Data+With+cURL+And+Wget>`_
- `Python <https://wiki.earthdata.nasa.gov/display/EL/How+To+Access+Data+With+Python>`_
- `Jupyter <https://github.com/nsidc/NSIDC-Data-Access-Notebook>`_
