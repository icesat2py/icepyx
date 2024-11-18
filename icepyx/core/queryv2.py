"""Icepyx v2 work-in-progress query module.

This module is a work-in-progress and re-implements the core functionality of
`icepyx.Query` using `earthaccess` and `harmony-py` in preparation for NSIDC's
decommissioning of the ECS-based ordering system. See the
`HARMONY_MIGRATION_NOTES` for more details.

The intent is to have the `QueryV2` class replace the existing, v1 `Query`
class. Once core functionality is implemented, relevant "V2" classes/functions
can be renamed and the v1 versions removed.
"""

from icepyx.core.query import BaseQuery


class QueryV2(BaseQuery): ...
