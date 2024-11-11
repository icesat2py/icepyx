from typing import Final

import requests

from icepyx.core.urls import COLLECTION_SEARCH_BASE_URL

CMR_PROVIDER: Final = "NSIDC_CPRD"


def get_concept_id(*, product: str, version: str) -> str:
    response = requests.get(
        COLLECTION_SEARCH_BASE_URL,
        params={
            "short_name": product,
            "version": version,
            "provider": CMR_PROVIDER,
        },
    )
    metadata = response.json()["feed"]["entry"]

    if len(metadata) != 1:
        raise RuntimeError(f"Expected 1 result from CMR, received {metadata}")

    return metadata[0]["id"]


# TODO: Extract CMR collection query from granules.py
