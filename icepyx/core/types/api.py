from typing import TypedDict, Union

from pydantic import BaseModel
from typing_extensions import NotRequired

CMRParamsBase = TypedDict(
    "CMRParamsBase",
    {
        "short_name": str,
        "version": str,
        "page_size": int,
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


class HarmonyCoverageAPIParamsBase(BaseModel): ...
