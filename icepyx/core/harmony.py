from typing import Any

import requests

from icepyx.core.urls import CAPABILITIES_BASE_URL


def get_capabilities(concept_id: str) -> dict[str, Any]:
    response = requests.get(
        CAPABILITIES_BASE_URL,
        params={"collectionId": concept_id},
    )
    return response.json()
