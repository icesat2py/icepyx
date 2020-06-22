from pathlib import Path

import icepyx

data_home = Path("../data")
data_home.mkdir(exist_ok=True)

# Three ways to pass variables

if 0:

    # 1) User specifies full path and the name it wants
    # for each extracted var in the reduced files (dict input).

    variables = {
        "lon_1l": "/gt1l/land_ice_segments/longitude",
        "lat_1l": "/gt1l/land_ice_segments/latitude",
        "h_1l": "/gt1l/land_ice_segments/h_li",
    }

elif 0:

    # 2) User specifies full paths and the code will
    # name each variable in a "smart" way (list input).

    variables = [
        "/gt1l/land_ice_segments/longitude",
        "/gt1l/land_ice_segments/latitude",
        "/gt1l/land_ice_segments/h_li",
    ]

else:

    # 3) User specifies key-names that map to variables in the
    # files. These are defined by us in the code (list input).

    variables = ["lon", "lat", "height"]


if 0:

    # Remote, for testing that works independently of local.

    region = icepyx.icesat2data.Icesat2Data(
        dataset="ATL06",
        spatial_extent=[-102, -76, -98, -74.5],
        date_range=["2019-06-18", "2019-06-25"],
        start_time="03:30:00",
        end_time="21:30:00",
        version="003",
    )

    print(region.dataset)
    print(region.dates)
    print(region.start_time)
    print(region.end_time)
    print(region.dataset_version)
    print(region.spatial_extent)
    print(region.avail_granules())

else:

    # Local, operations on existing data files locally.

    region = icepyx.icesat2data.Icesat2Data(files=data_home)

    print(region.path)
    print(region.files)

    xyz = region.get_vars(variables, outdir=data_home / "reduced")

    xyz.info()
    xyz.print_vars()


"""
>>> python get-vars.py
/Users/paolofer/code/icepyx/icepyx/data
[PosixPath('/Users/paolofer/code/icepyx/icepyx/data/ATL06_20190101003047_00540212_209_01.h5'), PosixPath('/Users/paolofer/code/icepyx/icepyx/data/ATL06_20190101002504_00540211_209_01.h5'), PosixPath('/Users/paolofer/code/icepyx/icepyx/data/ATL06_20190101001723_00540210_209_01.h5')]

Input files:
 ['ATL06_20190101003047_00540212_209_01.h5', 'ATL06_20190101002504_00540211_209_01.h5', 'ATL06_20190101001723_00540210_209_01.h5']

Output files:
 ['ATL06_20190101003047_00540212_209_01.h5_reduced', 'ATL06_20190101002504_00540211_209_01.h5_reduced', 'ATL06_20190101001723_00540210_209_01.h5_reduced']

Data folder:
 /Users/paolofer/code/icepyx/icepyx/data/reduced

Variables:
 ['lon', 'lat', 'height']

File variables:
height
lat
lon
"""
