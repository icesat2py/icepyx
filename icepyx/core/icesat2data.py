from icepyx.core.exceptions import DeprecationError


class Icesat2Data:
    def __init__(
        self,
    ):
        DeprecationError(
            "DEPRECATED. Please use icepyx.Query to create a download data object (all other functionality is the same)",
        )
