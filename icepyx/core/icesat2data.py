import warnings


class Icesat2Data:
    def __init__(self,):

        warnings.filterwarnings("always")
        warnings.warn(
            "Depricated. Please use icepyx.Query to create a download data object (all other functionality is the same)",
            DepricationWarning,
        )
