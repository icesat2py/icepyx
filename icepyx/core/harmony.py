from typing import Any

import harmony


def get_capabilities(concept_id: str) -> dict[str, Any]:
    capabilities_request = harmony.CapabilitiesRequest(concept_id=concept_id)
    # TODO: This will work if the user has a .netrc file available but the other
    # auth options might fail. We might need to add harmony client auth to the
    # icepyx auth package.
    harmony_client = harmony.Client()
    response = harmony_client.submit(capabilities_request)

    return response
