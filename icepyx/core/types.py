from __future__ import annotations

from typing import Literal, TypedDict, Union

from typing_extensions import NotRequired

IcesatProductShortName = Literal[
    "ATL01",
    "ATL02",
    "ATL03",
    "ATL04",
    "ATL06",
    "ATL07",
    "ATL07QL",
    "ATL08",
    "ATL09",
    "ATL09QL",
    "ATL10",
    "ATL11",
    "ATL12",
    "ATL13",
    "ATL14",
    "ATL15",
    "ATL16",
    "ATL17",
    "ATL19",
    "ATL20",
    "ATL21",
    "ATL23",
]

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


CMRParams = Union[CMRParamsWithBbox, CMRParamsWithPolygon]


class EGISpecificParamsBase(TypedDict):
    """Common parameters for searching, ordering, or downloading from EGI.

    See: https://wiki.earthdata.nasa.gov/display/SDPSDOCS/EGI+Programmatic+Access+Documentation

    EGI shares parameters with CMR, so this data is used in conjunction with CMRParams
    to build EGI requests.

    TODO: Validate more strongly (with Pydantic and its annotated types?
    https://docs.pydantic.dev/latest/concepts/types/#composing-types-via-annotated):

    * version is 3 digits
    * 0 < page_size <= 2000
    """

    short_name: IcesatProductShortName  # alias: "product"
    version: str
    page_size: int  # default 2000
    page_num: int  # default 0


class EGISpecificParamsSearch(EGISpecificParamsBase):
    """Parameters for interacting with EGI."""


class EGISpecificParamsDownload(EGISpecificParamsBase):
    """Parameters for ordering from EGI.

    TODO: Validate more strongly (with Pydantic?): page_num >=0.
    """

    request_mode: Literal["sync", "async", "stream"]  # default "async"
    include_meta: Literal["Y", "N"]  # default "Y"
    client_string: Literal["icepyx"]  # default "icepyx"
    # token, email


class EGIParamsSubsetBase(TypedDict):
    """Parameters for subsetting with EGI."""

    time: NotRequired[str]
    format: NotRequired[str]
    projection: NotRequired[str]
    projection_parameters: NotRequired[str]
    Coverage: NotRequired[str]


class EGIParamsSubsetBbox(EGIParamsSubsetBase):
    bbox: str


class EGIParamsSubsetBoundingShape(EGIParamsSubsetBase):
    Boundingshape: str


EGIParamsSubset = Union[EGIParamsSubsetBbox, EGIParamsSubsetBoundingShape]

EGISpecificRequiredParams = Union[EGISpecificParamsSearch, EGISpecificParamsDownload]
