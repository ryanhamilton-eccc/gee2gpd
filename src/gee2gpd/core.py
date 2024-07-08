import ee
import geopandas as gpd

def img2feat(element: ee.Image) -> ee.feature.Feature:
    """converts image to feature"""
    data = ee.Image(element)
    # copy all properties from the src image to the dest feature
    geom = data.geometry()
    prop_names = data.propertyNames()
    props = data.toDictionary(prop_names)
    return ee.Feature(geom, props)


def ic2fc(
    image_collection: ee.ImageCollection,
) -> ee.featurecollection.FeatureCollection:
    """handles the conversion of image collection to a feature collection"""
    ic_to_list = image_collection.toList(image_collection.size())
    # convert each element to a feaute ee.List[ee.Feature]
    feat_list = ic_to_list.map(img2feat)
    return ee.FeatureCollection(feat_list)


def fc2gdf(feature_collection: ee.FeatureCollection):
    geojson = feature_collection.getInfo()
    return gpd.GeoDataFrame.from_features(geojson['features'])


def image_collection_to_dataframe(collection: ee.ImageCollection) -> gpd.GeoDataFrame:
    """converts the collection and converts to geo data frame"""
    try:
        data = ic2fc(collection)
        data = fc2gdf(data)
    except ee.EEException as e:
        return e

    return data




