import copy

import earthaccess


class EarthdataAuthMixin():
    """
    This class stores methods related to logging into Earthdata. It is inherited by
    any other module that requires authentication.
    """
    def __init__(self, auth=None):
        self._auth = copy.deepcopy(auth)
        # initializatin of session and s3 creds is not allowed because those are generated
        # from the auth object
        self._session = None
        self._s3login_credentials = None

    def __str__(self):
        if self.session:
            repr_string = "EarthdataAuth obj with session initialized"
        else:
            repr_string = "EarthdataAuth obj without session initialized"
        return repr_string

    @property
    def auth(self):
        # Only login the first time .auth is accessed
        if self._auth is None:
            self._auth = earthaccess.login()
        return self._auth

    @property
    def session(self):
        # Only generate a session the first time .session is accessed
        if self._session is None:
            if self._auth is None:
                self._auth = earthaccess.login()
            if self._auth.authenticated:
                self._session = self._auth.get_session()
        return self._session

    @property
    def s3login_credentials(self):
        # Only generate s3login_credentials the first time credentials are accessed
        # TODO what if a user needs to regenerate after an hour?
        if self._s3login_credentials is None:
            if self._auth is None:
                self._auth = earthaccess.login()
            if self._auth.authenticated:
                self._s3login_credentials = self._auth.get_s3_credentials(daac="NSIDC")
        return self._s3login_credentials

    def earthdata_login(self, uid=None, email=None, s3token=False, **kwargs) -> None:
        """
        Authenticate with NASA Earthdata to enable data ordering and download.

        Generates the needed authentication sessions and tokens, including for cloud access.
        Authentication is completed using the [earthaccess library](https://nsidc.github.io/earthaccess/).
        Methods for authenticating are:
            1. Storing credentials as environment variables ($EARTHDATA_LOGIN and $EARTHDATA_PASSWORD)
            2. Entering credentials interactively
            3. Storing credentials in a .netrc file (not recommended for security reasons)
        More details on using these methods is available in the [earthaccess documentation](https://nsidc.github.io/earthaccess/tutorials/restricted-datasets/#auth).
        The input parameters listed here are provided for backwards compatibility;
        before earthaccess existed, icepyx handled authentication and required these inputs.
        DevNote: Maintained for backward compatibility

        Parameters
        ----------
        uid : string, default None
            Deprecated keyword for Earthdata login user ID.
        email : string, default None
            Deprecated keyword for backwards compatibility.
        s3token : boolean, default False
            Deprecated keyword to generate AWS s3 ICESat-2 data access credentials
        kwargs : key:value pairs
            Keyword arguments to be passed into earthaccess.login().

        Examples
        --------
        >>> reg_a = ipx.Query('ATL06',[-55, 68, -48, 71],['2019-02-20','2019-02-28']) # doctest: +SKIP
        >>> reg_a.earthdata_login() # doctest: +SKIP
        Enter your Earthdata Login username: ___________________

        EARTHDATA_USERNAME and EARTHDATA_PASSWORD are not set in the current environment, try setting them or use a different strategy (netrc, interactive)
        No .netrc found in /Users/username

        """

        auth = earthaccess.login(**kwargs)
        if auth.authenticated:
            self._auth = auth
            self._session = auth.get_session()

        if s3token == True:
            self._s3login_credentials = auth.get_s3_credentials(daac="NSIDC")

        if uid != None or email != None:
            warnings.warn(
                "The user id (uid) and/or email keyword arguments are no longer required.",
                DeprecationWarning,
            )
