from __future__ import annotations

from typing import Literal, TypedDict

from typing_extensions import NotRequired

CMRParamsBase = TypedDict(
    "CMRParamsBase",
    {
        "temporal": NotRequired[str],
        "options[readable_granule_name][pattern]": NotRequired[str],
        "options[spatial][or]": NotRequired[str],
        "readable_granule_name[]": NotRequired[str],
    },
)


class CMRParamsWithBbox(CMRParamsBase):
    bounding_box: str


class CMRParamsWithPolygon(CMRParamsBase):
    polygon: str


CMRParams = CMRParamsWithBbox | CMRParamsWithPolygon


class EGISpecificParamsBase(TypedDict):
    """Common parameters for searching, ordering, or downloading from EGI.

    See: https://wiki.earthdata.nasa.gov/display/SDPSDOCS/EGI+Programmatic+Access+Documentation

    EGI shares parameters with CMR, so this data is used in conjunction with CMRParams
    to build EGI requests.

    TODO: Validate more strongly (with Pydantic and its annotated types?
    https://docs.pydantic.dev/latest/concepts/types/#composing-types-via-annotated):

    * short_name is `ATL##` (or Literal list of values?)
    * version is 1-3 digits
    * 0 < page_size <= 2000
    """

    short_name: str  # alias: "product"
    version: str
    page_size: int  # default 2000
    page_num: int  # default 0


class EGISpecificParamsSearch(EGISpecificParamsBase):
    """Parameters for searching through EGI."""


class EGISpecificParamsOrder(EGISpecificParamsBase):
    """Parameters for ordering through EGI."""

    # TODO: Does this type need page_* attributes?


class EGISpecificParamsDownload(EGISpecificParamsBase):
    """Parameters for ordering from EGI.

    TODO: Validate more strongly (with Pydantic?): page_num >=0.
    """

    request_mode: Literal["sync", "async", "stream"]  # default "async"
    include_meta: Literal["Y", "N"]  # default "Y"
    client_string: Literal["icepyx"]  # default "icepyx"
    # token, email


class EGISpecificParamsSubset(EGISpecificParamsBase):
    """Parameters for subsetting with EGI."""


EGISpecificParams = (
    EGISpecificParamsSearch | EGISpecificParamsDownload | EGISpecificParamsSubset
)
