import earthaccess


class EarthdataAuth():
    """
    This class stores methods related to logging into Earthdata. It is inherited by
    any other module that requires authentication.
    """
    def __init__(
        self, 
        _session=None, 
        _s3login_credentials=None,
    ):
        self._session = _session
        self._s3login_credentials = _s3login_credentials

    def __str__(self):
        if self._session:
            repr_string = "EarthdataAuth obj with session initialized"
        else:
            repr_string = "EarthdataAuth obj without session initialized"
        return repr_string
    
    def session_started():
        # return True/False if there is a session
        pass

    def s3credentials_created():
        # return True/False if there are s3 credentials
        pass

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
