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
import json

from fsspec.utils import tempfile
import harmony
import earthaccess

from icepyx.core.harmony import HarmonyApi, HarmonyTemporal
from icepyx.core.base_query import BaseQuery
import icepyx.core.temporal as tp
import icepyx.core.APIformatting as apifmt

from icepyx.core.granules import Granules, gran_IDs
import icepyx.core.validate_inputs as val

from icepyx.core.types import CMRParams


class Query(BaseQuery):
    _temporal: Union[tp.Temporal, None]
    _CMRparams: apifmt.CMRParameters

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.harmony_api = HarmonyApi()

        # Ensure that the `_temporal` attr is set. This simplifies checking if
        # temporal parameters has been passed. Instead of using `hasattr`, we
        # can just check for `None`.
        if not hasattr(self, "_temporal"):
            self._temporal = None  # type: ignore[reportIncompatibleVariableOverride]

        cycles = kwargs.get("cycles")
        tracks = kwargs.get("tracks")
        if cycles or tracks:
            # get lists of available ICESat-2 cycles and tracks
            self._cycles = val.cycles(cycles)
            self._tracks = val.tracks(tracks)
            # create list of CMR parameters for granule name
            self._readable_granule_name = apifmt._fmt_readable_granules(
                self._prod, cycles=self.cycles, tracks=self.tracks
            )


    @property
    def cycles(self):
        """
        Return the unique ICESat-2 orbital cycle.

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.cycles
        ['No orbital parameters set']

        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71], cycles=['03','04'], tracks=['0849','0902'])
        >>> reg_a.cycles
        ['03', '04']
        """
        if not hasattr(self, "_cycles"):
            return ["No orbital parameters set"]
        else:
            return sorted(set(self._cycles))

    @property
    def tracks(self):
        """
        Return the unique ICESat-2 Reference Ground Tracks

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.tracks
        ['No orbital parameters set']

        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71], cycles=['03','04'], tracks=['0849','0902'])
        >>> reg_a.tracks
        ['0849', '0902']
        """
        if not hasattr(self, "_tracks"):
            return ["No orbital parameters set"]
        else:
            return sorted(set(self._tracks))


    def _get_concept_id(self, product, version) -> Union[str, None]:
        collections = earthaccess.search_datasets(short_name=product,
                                                  version=version,
                                                  cloud_hosted=True)
        if collections:
            return collections[0].concept_id()
        else:
            return None

    def show_custom_options(self) -> None:
        """
        Display customization/subsetting options available for this product.

        Parameters
        ----------
        dictview : boolean, default False
            Show the variable portion of the custom options list as a dictionary with key:value
            pairs representing variable:paths-to-variable rather than as a long list of full
            variable paths.

        """
        if self.concept_id:

            capabilities = self.harmony_api.get_capabilities(concept_id=self.concept_id)
            print(json.dumps(capabilities, indent=2))
        return None


    @property
    def CMRparams(self) -> CMRParams:
        """
        Display the CMR key:value pairs that will be submitted.
        It generates the dictionary if it does not already exist.

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.CMRparams
        {'temporal': '2019-02-20T00:00:00Z,2019-02-28T23:59:59Z',
        'bounding_box': '-55.0,68.0,-48.0,71.0'}
        """

        if not hasattr(self, "_CMRparams"):
            self._CMRparams = apifmt.Parameters("CMR")
        # print(self._CMRparams)
        # print(self._CMRparams.fmted_keys)
        

        # dictionary of optional CMR parameters
        kwargs = {}
        kwargs["concept_id"] = self._get_concept_id(self.product, None)

        # temporal CMR parameters
        if hasattr(self, "_temporal") and self.product != "ATL11" and self._temporal:
            kwargs["start"] = self._temporal._start
            kwargs["end"] = self._temporal._end
        # granule name CMR parameters (orbital or file name)
        # DevGoal: add to file name search to optional queries
        if hasattr(self, "_readable_granule_name"):
            kwargs["options[readable_granule_name][pattern]"] = "true"
            kwargs["options[spatial][or]"] = "true"
            kwargs["readable_granule_name[]"] = self._readable_granule_name

        if self._CMRparams.fmted_keys == {}:
            self._CMRparams.build_params(
                extent_type=self._spatial._ext_type,
                spatial_extent=self._spatial.fmt_for_CMR(),
                **kwargs,
            )

        return self._CMRparams.fmted_keys
    
    @property
    def granules(self):
        """
        Return the granules object, which provides the underlying functionality for searching, ordering,
        and downloading granules for the specified product.
        Users are encouraged to use the built-in wrappers
        rather than trying to access the granules object themselves.

        See Also
        --------
        avail_granules
        order_granules
        download_granules
        granules.Granules

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28']) # doctest: +SKIP
        >>> reg_a.granules # doctest: +SKIP
        <icepyx.core.granules.Granules at [location]>
        """

        if not hasattr(self, "_granules") or self._granules is None:
            self._granules = Granules()

        return self._granules

    # DevGoal: check to make sure the see also bits of the docstrings work properly in RTD
    def avail_granules(self, ids=False, cycles=False, tracks=False, cloud=False):
        """
        Obtain information about the available granules for the query
        object's parameters. By default, a complete list of available granules is
        obtained and stored in the object, but only summary information is returned.
        Lists of granule IDs, cycles and RGTs can be obtained using the boolean triggers.

        Parameters
        ----------
        ids : boolean, default False
            Indicates whether the function should return a list of granule IDs.

        cycles : boolean, default False
            Indicates whether the function should return a list of orbital cycles.

        tracks : boolean, default False
            Indicates whether the function should return a list of RGTs.

        cloud : boolean, default False
            Indicates whether the function should return data available in the cloud.
            Note: except in rare cases while data is in the process of being appended to,
            data available in the cloud and for download via on-premesis will be identical.

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28'])
        >>> reg_a.avail_granules()
        {'Number of available granules': 4,
        'Average size of granules (MB)': np.float64(55.166646003723145),
        'Total size of all granules (MB)': 220.66658401489258}

        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-23'])
        >>> reg_a.avail_granules(ids=True)
        [['ATL06_20190221121851_08410203_006_01.h5', 'ATL06_20190222010344_08490205_006_01.h5']]
        >>> reg_a.avail_granules(cycles=True)
        [['02', '02']]
        >>> reg_a.avail_granules(tracks=True)
        [['0841', '0849']]
        """

        #         REFACTOR: add test to make sure there's a session
        if not hasattr(self, "_granules"):
            self.granules
        try:
            self.granules.avail
        except AttributeError:
            self.granules.get_avail(self.CMRparams)

        if ids or cycles or tracks or cloud:
            # list of outputs in order of ids, cycles, tracks, cloud
            return gran_IDs(
                self.granules.avail,
                ids=ids,
                cycles=cycles,
                tracks=tracks,
                cloud=cloud,
            )
        else:
            return self.granules.avail



    def _order_subset_granules(self) -> str:
        concept_id = self._get_concept_id(
            product=self._prod,
            version=self._version,
        )

        if concept_id is None:
            raise ValueError(f"Could not find concept ID for {self._prod} v{self._version}")

        harmony_temporal = None
        if self._temporal:
            # TODO: this assumes there will always be a start and stop
            # temporal range. Harmony can accept start without stop and
            # vice versa.
            harmony_temporal = HarmonyTemporal(
                start=self._temporal.start,
                stop=self._temporal.end,
            )

        # TODO: think more about how this can be DRYed out. We call
        # `place_order` based on the user spatial input. The bounding box case
        # is simple, but polygons are more complicated because `harmony-py`
        # expects a shapefile (e.g,. geojson) to exist on disk.
        if self.spatial.extent_type == "bounding_box":
            # Bounding box case.
            return self.harmony_api.place_order(
                concept_id=concept_id,
                temporal=harmony_temporal,
                spatial=harmony.BBox(
                    w=self.spatial.extent[0],
                    s=self.spatial.extent[1],
                    e=self.spatial.extent[2],
                    n=self.spatial.extent[3],
                ),
            )
        else:
            # Polygons must be passed to `harmony-py` as a path to a valid
            # shapefile (json, geojson, kml, shz, or zip). Create a temporary
            # directory to store this file for the harmony order.
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Polygon
                df = self.spatial.extent_as_gdf
                # Use geojson to pass along to harmony. Icepyx supports formats
                # that harmony does not (e.g., `gpkg`). Harmony supports json,
                # geojson, kml, shz, zip.
                shapefile_path = str(Path(tmp_dir) / "harmony_spatial_subset.geojson")
                df.to_file(shapefile_path)

                return self.harmony_api.place_order(
                    concept_id=concept_id,
                    temporal=harmony_temporal,
                    shape=shapefile_path,
                )

    def get_granule_links(self, cloud_hosted=False) -> list[str]:
        links = []
        for granule in self.granules.avail:
            for link in granule["links"]:
                if cloud_hosted and link["rel"] == "http://esipfed.org/ns/fedsearch/1.1/s3#":
                    links.append(link["href"])
                elif link["rel"] == "http://esipfed.org/ns/fedsearch/1.1/data#":
                    if "type" in link and link["type"] in ["application/x-hdf5",
                                                           "application/x-hdfeos"]:
                        links.append(link["href"])
        return links


    def _order_whole_granules(self, cloud_hosted=False, path="./") -> None:
        """
        Downloads the whole granules for the query object. This is not an asnc operation
        and will block until the download is complete.

        Parameters
        ----------
        cloud_hosted : bool, default False
            If True, download the cloud-hosted version of the granules. Otherwise, download
            the on-premises version. We need to run the code in the AWS cloud (us-west-2)
        path : str, default "./"
            The local directory to download the granules to.

        """
        
        links = self.get_granule_links(cloud_hosted=cloud_hosted)
        earthaccess.download(links, local_path=path)


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
            self._order_subset_granules()
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
