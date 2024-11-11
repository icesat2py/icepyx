from typing import Any

import harmony

from icepyx.core.auth import EarthdataAuthMixin


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
