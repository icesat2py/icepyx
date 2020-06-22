from pathlib import Path
import icepyx

data_home = Path("../data")
data_home.mkdir(exist_ok=True)

files = list(data_home.glob("*.h5"))

# Pine Island Glacier

vardict = {
    'lon_1l': "/gt1l/land_ice_segments/longitude",
    'lat_1l': "/gt1l/land_ice_segments/latitude",
    'h_1l': "/gt1l/land_ice_segments/h_li",
}

if 0:
    # Remote
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
    # Local
    region = icepyx.icesat2data.Icesat2Data(files='../data')

    print(region.path)
    print(region.files)
    print()

    # xyz = region.get_vars(vardict, outdir='../data/reduced')

    # print(xyz.files)
    # print(xyz.variables)
    # print(xyz.outdir)
    # print()

    # xyz.info()
    # xyz.print_vars()


# print(region.show_custom_options(dictview=True))

# region.visualize_spatial_extent()

# region.dataset_summary_info()

# region.get_vars(ifile)

# region.print_vars(ifile)
