"""Icepyx v2 work-in-progress query module.

This module is a work-in-progress and re-implements the core functionality of
`icepyx.Query` using `earthaccess` and `harmony-py` in preparation for NSIDC's
decommissioning of the ECS-based ordering system. See the
`HARMONY_MIGRATION_NOTES` for more details.

The intent is to have the `QueryV2` class replace the existing, v1 `Query`
class. Once core functionality is implemented, relevant "V2" classes/functions
can be renamed and the v1 versions removed.
"""

from pathlib import Path
from typing import Union

from icepyx.core.cmr import get_concept_id
from icepyx.core.harmony import HarmonyApi, HarmonyTemporal
from icepyx.core.query import BaseQuery
import icepyx.core.temporal as tp


class QueryV2(BaseQuery):
    _temporal: Union[tp.Temporal, None]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.harmony_api = HarmonyApi()

        # Ensure that the `_temporal` attr is set. This simplifies checking if
        # temporal parameters has been passed. Instead of using `hasattr`, we
        # can just check for `None`.
        if not hasattr(self, "_temporal"):
            self._temporal = None  # type: ignore[reportIncompatibleVariableOverride]

    def _order_subset_granules(self, short_name: str, version: str, **kwargs) -> str:
        concept_id = get_concept_id(
            product=short_name,
            version=version,
        )

        # Place the order.
        job_id = self.harmony_api.place_order(concept_id=concept_id, **kwargs)

        return job_id

    def _order_whole_granules(self):
        # This may not actually be necessary. Whole granules are just downloaded
        # from their downloadable URL link using earthaccess, so this can be a
        # noop. It will just be harmony (subset) orders that require an order
        # step.
        raise NotImplementedError

    def order_granules(self, subset=True):
        """
        Place an order for the available granules for the query object.

        Parameters
        ----------
        subset :
            Apply subsetting to the data order using harmony, returning only data that meets the
            subset parameters. Spatial and temporal subsetting based on the input parameters happens
            by default when subset=True, but additional subsetting options are available.
            Spatial subsetting returns all data that are within the area of interest (but not complete
            granules. This eliminates false-positive granules returned by the metadata-level search)

        See Also
        --------
        harmony.place_order

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28']) # doctest: +SKIP
        >>> reg_a.order_granules() # doctest: +SKIP
        Harmony job ID:  931355e8-0005-4dff-9c76-7903a5be283d
        [order status output]
        Harmony provided these error messages:
        [if any were returned from the harmony subsetter, e.g. No data found that matched subset constraints.]
        Your harmony order is:  complete
        """
        if subset:
            if self._temporal:
                # TODO: this assumes there will always be a start and stop
                # temporal range. Harmony can accept start without stop and
                # vice versa.
                harmony_temporal = HarmonyTemporal(
                    start=self._temporal.start,
                    stop=self._temporal.end,
                )
            else:
                harmony_temporal = None

            self._order_subset_granules(
                short_name=self._prod,
                version=self._version,
                temporal=harmony_temporal,
                **self.spatial.fmt_for_harmony(),
            )
        else:
            self._order_whole_granules()

    def download_granules(
        self,
        path: Path,
        subset: bool = True,
        restart: bool = False,
        overwrite: bool = False,
    ) -> None:
        # Order granules based on user selections if restart is False and there
        # are no job IDs registered by the harmony API
        if not restart:
            if subset:
                if not self.harmony_api.job_ids:
                    self.order_granules(subset=subset)
            else:
                # Non-subset orders are not implemented yet.
                raise NotImplementedError

        # Download logic
        if subset:
            self.harmony_api.download_granules(download_dir=path, overwrite=overwrite)
        else:
            raise NotImplementedError
