import os

import pytest
import requests

import earthaccess

from icepyx.core.auth import EarthdataAuthMixin


@pytest.fixture()
def auth_instance():
    """
    An EarthdatAuthMixin object for each of the tests. Default scope is function
    level, so a new instance should be created for each of the tests.
    """
    return EarthdataAuthMixin()


# Test that .session creates a session
@pytest.mark.skipif(os.getenv("TRAVIS"), "Skipping this test on Travis CI.")
def test_get_session(auth_instance):
    print(os.environ)
    assert isinstance(auth_instance.session, requests.sessions.Session)


# Test that .s3login_credentials creates a dict with the correct keys
@pytest.mark.skipif(
    os.environ.get("TRAVIS") == "true", "Skipping this test on Travis CI."
)
def test_get_s3login_credentials(auth_instance):
    assert isinstance(auth_instance.s3login_credentials, dict)
    expected_keys = set(
        ["accessKeyId", "secretAccessKey", "sessionToken", "expiration"]
    )
    assert set(auth_instance.s3login_credentials.keys()) == expected_keys


# Test that earthdata_login generates an auth object
@pytest.mark.skipif(
    os.environ.get("TRAVIS") == "true", "Skipping this test on Travis CI."
)
def test_login_function(auth_instance):
    assert isinstance(auth_instance.auth, earthaccess.auth.Auth)
    assert auth_instance.auth.authenticated
