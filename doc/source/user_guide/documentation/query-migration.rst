Query Class Migration to Earthaccess Guide
==========================================

In an effort to streamline ICESat-2 and related dataset workflows,
the icepyx, `earthaccess <>`_, and `SlideRule <>`_ development teams
are working together to reduce duplicated functionality.

TODO: Make and insert figure(s) showing duplicated functionality for querying between icepyx and earthaccess.

Given the breaking changes required for icepyx to adapt to `changes in the NSIDC backend <>`_,
we thought it would be an opportune time to implement this big step towards streamlined data access.

This document aims to ease the transition process by showing the prior icepyx functionality
matched with the new, recommended earthaccess functionality.
We are striving to make sure all features are available,
but please let us know if you're finding it difficult to migrate specific tasks.


Table of icepyx functions and their recommended earthaccess equivalents

+------------------------+------------+----------+----------+
| icepyx v1.x function   | earthaccess function  | Header 3 | Header 4 |
| (header rows optional) |                       |          |          |
+========================+============+==========+==========+
| ipx.Query   | column 2   | column 3 | column 4 |
+------------------------+------------+----------+----------+
| body row 2             | ...        | ...      |          |
+------------------------+------------+----------+----------+


Dev Questions and Considerations:
- should ipx.Query still exist, and simply return an earthaccess query object instead?
    - this could save users from having to totally rewrite their code
    - the recommended pathway would still be to use earthaccess directly

- what would need to be implemented in earthaccess to make the rest of icepyx easily work?

- it would also be great to have lots of code examples (perhaps some here in addition to updating all the notebooks?)
that show equivalent earthaccess searches

Notes as exploration happens:
-


icepyx Attributes
-----------------

   Query.CMRparams
   Query.cycles
   Query.dates
   Query.end_time
   Query.granules
   Query.order_vars
   Query.product
   Query.product_version
   Query.reqparams
   Query.spatial
   Query.spatial_extent
   Query.subsetparams
   Query.start_time
   Query.temporal
   Query.tracks

icepyx Methods
--------------

   Query.avail_granules
   Query.download_granules (earthaccess does not have subsetting)
   Query.latest_version
   Query.order_granules (earthaccess does not have subsetting - don't need orders there)
   Query.product_all_info
   Query.product_summary_info
   Query.show_custom_options
   Query.visualize_spatial_extent --> currently broken
   Query.visualize_elevation --> currently broken
