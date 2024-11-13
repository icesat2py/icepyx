import datetime as dt
from typing import Any, NotRequired, TypedDict, Union

import harmony

from icepyx.core.auth import EarthdataAuthMixin


class HarmonyTemporal(TypedDict):
    start: NotRequired[dt.datetime]
    stop: NotRequired[dt.datetime]


class HarmonyApi(EarthdataAuthMixin):
    def __init__(self):
        # initialize authentication properties
        EarthdataAuthMixin.__init__(self)
        self.harmony_client = harmony.Client(
            auth=(
                self.auth.username,
                self.auth.password,
            ),
        )

    def get_capabilities(self, concept_id: str) -> dict[str, Any]:
        capabilities_request = harmony.CapabilitiesRequest(concept_id=concept_id)
        response = self.harmony_client.submit(capabilities_request)

        return response

    def place_order(
        self,
        concept_id: str,
        # These are optional subset parameters
        bounding_box: Union[harmony.BBox, None] = None,
        temporal: Union[HarmonyTemporal, None] = None,
    ) -> str:
        """Places a Harmony order with the given parameters.

        Return a string representing a job ID.

        TODO/Question: it looks like this code will always use the provided
        parameters to do subsetting. Are there cases where we just want the data
        downloaded as whole granules? If so, we may need to use another API to
        do so?
        """
        collection = harmony.Collection(id=concept_id)
        request = harmony.Request(
            collection=collection,
            spatial=bounding_box,
            temporal=temporal,
        )

        if not request.is_valid():
            # TODO: consider more specific error class & message
            raise RuntimeError("Failed to create valid request")

        job_id = self.harmony_client.submit(request)

        return job_id

    def check_order_status(self, job_id: str) -> dict[str, Any]:
        status = self.harmony_client.status(job_id)
        return status
