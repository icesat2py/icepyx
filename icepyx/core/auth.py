import copy
import datetime

import earthaccess


class AuthenticationError(Exception):
    """
    Raised when an error is encountered while authenticating Earthdata credentials
    """


class EarthdataAuthMixin:
    """
    This mixin class generates the needed authentication sessions and tokens,
    including for NASA Earthdata cloud access.
    Authentication is completed using the [earthaccess library](https://nsidc.github.io/earthaccess/).
    Methods for authenticating are:
        1. Storing credentials as environment variables ($EARTHDATA_LOGIN and $EARTHDATA_PASSWORD)
        2. Entering credentials interactively
        3. Storing credentials in a .netrc file (not recommended for security reasons)
    More details on using these methods is available in the [earthaccess documentation](https://nsidc.github.io/earthaccess/tutorials/restricted-datasets/#auth).

    This class can be inherited by any other class that requires authentication.
    For example, the `Query` class inherits this one, and so a Query object has the
    `.session` property.

    The class can be created without any initialization parameters, and the properties will
    be populated when they are called.
    It can alternately be initialized with an
    earthaccess.auth.Auth object, which will then be used to create a session or
    s3login_credentials as they are called.

    Parameters
    ----------
    auth : earthaccess.auth.Auth, default None
        Optional parameter to initialize an object with existing credentials.

    Examples
    --------
    >>> a = EarthdataAuthMixin()
    >>> a.session # doctest: +SKIP
    >>> a.s3login_credentials # doctest: +SKIP
    """

    def __init__(self, auth=None):
        self._auth = copy.deepcopy(auth)
        # initialization of session and s3 creds is not allowed because those are generated
        # from the auth object
        self._session = None
        self._s3login_credentials = None
        self._s3_initial_ts = None  # timer for 1h expiration on s3 credentials

    def __str__(self) -> str:
        if self.session:
            repr_string = "EarthdataAuth obj with session initialized"
        else:
            repr_string = "EarthdataAuth obj without session initialized"
        return repr_string

    @property
    def auth(self):
        """
        Authentication object returned from earthaccess.login() which stores user authentication.
        """
        # Only login the first time .auth is accessed
        if self._auth is None:
            auth = earthaccess.login()
            # check for a valid auth response
            if auth.authenticated is False:
                raise AuthenticationError(
                    "Earthdata authentication failed. Check output for error message"
                )
            else:
                self._auth = auth

        return self._auth

    @property
    def session(self):
        """
        Earthaccess session object for connecting to Earthdata resources.
        """
        # Only generate a session the first time .session is accessed
        if self._session is None:
            self._session = self.auth.get_session()
        return self._session

    @property
    def s3login_credentials(self):
        """
        A dictionary which stores login credentials for AWS s3 access.
        This property is accessed if using AWS cloud data.

        Because s3 tokens are only good for one hour, this function will automatically check if an
        hour has elapsed since the last token use and generate a new token if necessary.
        """

        def set_s3_creds():
            """Store s3login creds from `auth`and reset the last updated timestamp"""
            self._s3login_credentials = self.auth.get_s3_credentials(daac="NSIDC")
            self._s3_initial_ts = datetime.datetime.now()

        # Only generate s3login_credentials the first time credentials are accessed, or if an hour
        # has passed since the last login
        if self._s3login_credentials is None or (
            datetime.datetime.now() - self._s3_initial_ts
        ) >= datetime.timedelta(hours=1):
            set_s3_creds()
        return self._s3login_credentials
