class QueryError(Exception):
    """
    Base class for Query object exceptions
    """

    pass


class NsidcQueryError(QueryError):
    """
    Raised when an error was returned from NSIDC during the query step."
    """

    def __init__(
        self, errmsg, msgtxt="An error was returned from NSIDC in regards to your query"
    ):
        self.errmsg = errmsg
        self.msgtxt = msgtxt
        super().__init__(self.msgtxt)

    def __str__(self):
        return f"{self.msgtxt}: {self.errmsg}"
