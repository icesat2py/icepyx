import pytest

from icepyx.core.read import Read
import icepyx.core.read as read


def test_source_str_given_as_list():
    ermesg = "You must enter your input as a string."
    with pytest.raises(AssertionError, match=ermesg):
        read._validate_source(["/path/to/valid/ATL06_file.py"])


# How do we test this? Do we need to, since it's just checking things for the user?
# def test_source_str_is_valid_file():
#     ermesg = "Your data source string is not a valid data source."
#     with pytest.raises(AssertionError, match=ermesg):
#         read._validate_source("/path/to/valid/ATL06_file.py", "/path/to/valid/dir")


# @pytest.mark.parametrize(
#     "n, exp",
#     [
#         (
#             1,
#             [
#                 "ATL06_20200702014158_01020810_004_01.h5",
#                 "ATL06_20200703011618_01170810_004_01.h5",
#             ],
#         ),
#         (
#             2,
#             [
#                 "ATL06_20200612151119_11920712_004_01.h5",
#                 "ATL06_20200616021517_12450710_004_01.h5",
#                 "ATL06_20200702014158_01020810_004_01.h5",
#                 "ATL06_20200703011618_01170810_004_01.h5",
#             ],
#         ),
#         (
#             3,
#             [
#                 "ATL06_20200612151119_11920712_004_01.h5",
#                 "ATL06_20200616021517_12450710_004_01.h5",
#                 "ATL06_20200702014158_01020810_004_01.h5",
#                 "ATL06_20200703011618_01170810_004_01.h5",
#             ],
#         ),
#     ],
# )
# def test_files_in_latest_cycles(n, exp):
#     files = [
#         "ATL06_20190710071617_01860412_004_01.h5",
#         "ATL06_20190713182016_02390410_004_01.h5",
#         "ATL06_20200612151119_11920712_004_01.h5",
#         "ATL06_20200616021517_12450710_004_01.h5",
#         "ATL06_20200702014158_01020810_004_01.h5",
#         "ATL06_20200703011618_01170810_004_01.h5",
#     ]
#     cycles = [8, 7, 4]
#     obs = vis.files_in_latest_n_cycles(files, cycles=cycles, n=n)
#     assert obs == exp
