from typing import Final

CMR_BASE_URL: Final = "https://cmr.earthdata.nasa.gov"
GRANULE_SEARCH_BASE_URL: Final = f"{CMR_BASE_URL}/search/granules"
COLLECTION_SEARCH_BASE_URL: Final = f"{CMR_BASE_URL}/search/collections.json"

# TODO: the harmony base url and capabilities URL will be handled by
# `harmony-py`: remove these constants.
HARMONY_BASE_URL: Final = "https://harmony.earthdata.nasa.gov"
CAPABILITIES_BASE_URL: Final = f"{HARMONY_BASE_URL}/capabilities"
ORDER_BASE_URL: Final = f"{HARMONY_BASE_URL}/...?"
DOWNLOAD_BASE_URL: Final = f"{HARMONY_BASE_URL}/...?"
