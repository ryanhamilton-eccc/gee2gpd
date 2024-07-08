import ee
import geopandas as gpd
from gee2gpd import core

ee.Initialize()
import helpers as hlp


def test_img2feat():
    image = ee.Image("LANDSAT/LC08/C02/T1_L2/LC08_040025_20130319")
    as_features = core.img2feat(image)
    expected_props = (
        image.propertyNames().removeAll(["system:bands", "system:band_names"]).getInfo()
    )
    actual_props = as_features.propertyNames().getInfo()

    assert actual_props == expected_props
    assert isinstance(as_features, ee.Feature)


def test_ic2fc():
    ic = hlp.fetch_l8sr_collection()
    fc = core.ic2fc(ic)

    assert isinstance(fc, ee.FeatureCollection)
    # check to make sure that this work properly with out any server side errors
    fc.first().getInfo()


def test_fc2gdf():
    ic = hlp.fetch_l8sr_collection()
    fc = core.ic2fc(ic)
    gdf = core.fc2gdf(fc)
    
    assert isinstance(gdf, gpd.GeoDataFrame)
    

def test_image_collection_to_dataframe():
    ic = hlp.fetch_l8sr_collection()
    gdf = core.image_collection_to_dataframe(ic)
    assert isinstance(gdf, gpd.GeoDataFrame)