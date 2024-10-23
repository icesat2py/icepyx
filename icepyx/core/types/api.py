from typing import Literal, TypedDict, Union

from typing_extensions import NotRequired
from pydantic import BaseModel

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


class HarmonyCoverageAPIParamsBase(BaseModel):
