"""
Integration tests for the spatial inputs and subsetting
within the Query class (and passed to Harmony)

See Also
--------

./test_query
"""

import datetime as dt
import logging
from pathlib import Path
import tempfile
import time

import geopandas as gpd
import pytest
import shapely

import icepyx as ipx
from icepyx.core.query import Query


@pytest.fixture()
def spatial_extent(request):
    extent_type = request.param
    xmin = -49.149
    ymin = 69.186
    xmax = -48.949
    ymax = 69.238
    if extent_type == "bounding_box":
        yield [xmin, ymin, xmax, ymax]
    elif extent_type == "polygon":
        yield [
            xmax,
            ymin,
            xmax,
            ymax,
            xmin,
            ymax,
            xmin,
            ymin,
            xmax,
            ymin,
        ]
    elif extent_type == "polygon_file":
        with tempfile.TemporaryDirectory() as tmp_dir:
            polygon_filepath = Path(tmp_dir) / "test_polygon.gpkg"
            gdf = gpd.GeoDataFrame(
                {"geometry": [shapely.box(xmin, ymin, xmax, ymax)]}, crs="EPSG:4326"
            )
            gdf.to_file(polygon_filepath)
            yield str(polygon_filepath)


# https://docs.pytest.org/en/8.3.x/example/parametrize.html#indirect-parametrization
@pytest.mark.downloads_data
@pytest.mark.parametrize(
    "spatial_extent", ["bounding_box", "polygon", "polygon_file"], indirect=True
)
def test_spatial_and_temporal_subset(tmp_path, spatial_extent):
    """Test simple harmony subset order with spatial and temporal subsetting.

    This test is setup to be parameterized for three different spatial inputs: a
    bounding box, a polygon, and a geopackage located on disk. Each spatial
    input represents the same area of interest, just in a different format.
    This is important because bounding box inputs are handled differentely than
    polygons when ordering form harmony. The geopackage input ensures that the
    code properly handles user input that is not supported by harmony (harmony
    does not accept geopackages as input, so we do a conversion to geojson
    behind the scenes!)
    """
    print(f"Spatial extent: {spatial_extent}")
    q = Query(
        product="ATL06",
        version="006",
        spatial_extent=spatial_extent,
        date_range={
            "start_date": dt.datetime(2024, 4, 1, 0, 0, 0),
            "end_date": dt.datetime(2024, 4, 3, 0, 0, 0),
        },
    )

    order = q.order_granules(subset=True)
    assert order is not None
    assert order.type == "subset"
    while True:
        status = order.status()
        print(f"Order status: {status['status']}")
        if (
            status["status"] == "successful"
            or status["status"] == "complete_with_errors"
        ):
            break
        elif status["status"] == "failed":
            raise Exception("Order failed")
        else:
            # Sleep for a bit to avoid hammering the server
            logging.info("Order is still processing...")
            time.sleep(5)
    files = order.download_granules(path=tmp_path, overwrite=True)
    assert isinstance(files, list)

    # Query should result in download of one subsetted granule.
    assert len(list(tmp_path.glob("*.h5"))) == 1

    # Ensure that the result is readable by the `Read` class
    reader = ipx.Read(tmp_path)
    reader.variables.append(
        beam_list=["gt1l", "gt3r"], var_list=["h_li", "latitude", "longitude"]
    )

    ds = reader.load()
    assert "h_li" in ds
