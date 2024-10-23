ISSUE_REPORTING_INSTRUCTIONS = (
    "If you are a user seeing this message, the developers of this software have made a"
    " mistake! Please report the full error traceback in the icepyx GitHub repository:"
    " <https://github.com/icesat2py/icepyx/issues/new>"
)


class DeprecationError(Exception):
    """
    Class raised for use of functionality that is no longer supported by icepyx.
    """


class QueryError(Exception):
    """
    Base class for Query object exceptions
    """


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


class TypeGuardException(Exception):
    """
    Should never be raised at runtime.

    Used in cases where a runtime check is not desired, but we want to add a "type guard"
    (https://github.com/microsoft/pyright/blob/main/docs/type-concepts-advanced.md#type-guards)
    to give the type checker more information.
    """

    def __str__(self):
        return ISSUE_REPORTING_INSTRUCTIONS


class ExhaustiveTypeGuardException(TypeGuardException):
    """
    Should never be raised at runtime.

    Used exclusively in cases where the typechecker needs a typeguard to tell it that a
    check is exhaustive.
    """


class RefactoringException(Exception):
    def __str__(self):
        return (
            "This code is being refactored."
            " The code after this exception is expected to require major changes."
        )
