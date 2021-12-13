import icepyx
import pytest


@pytest.fixture(autouse=True)
def add_ipx(doctest_namespace):
    doctest_namespace["ipx"] = icepyx
