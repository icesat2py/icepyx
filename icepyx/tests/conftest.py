import os
import pytest
from unittest import mock

# PURPOSE: mock environmental variables
@pytest.fixture(scope="session", autouse=True)
def mock_settings_env_vars():
    with mock.patch.dict(
        "os.environ",
        {
            "EDL_USERNAME": "icepyx_devteam",
            "EDL_PASSWORD": "fake_earthdata_password",
            "EARTHDATA_USERNAME": "icepyx_devteam2",
            "EARTHDATA_PASSWORD": "fake_earthdata_password2",
            "EARTHDATA_EMAIL": "icepyx.dev@gmail.com",
        },
    ):
        yield


@pytest.fixture(scope="session")
def username():
    return os.environ.get("EDL_USERNAME")


@pytest.fixture(scope="session")
def password():
    return os.environ.get("EDL_PASSWORD")


@pytest.fixture(scope="session")
def dep_username():
    return os.environ.get("EARTHDATA_USERNAME")


@pytest.fixture(scope="session")
def dep_password():
    return os.environ.get("EARTHDATA_PASSWORD")


@pytest.fixture(scope="session")
def email():
    return os.environ.get("EARTHDATA_EMAIL")
