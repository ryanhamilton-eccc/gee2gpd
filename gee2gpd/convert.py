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


def ic_to_dataframe(collection: ee.ImageCollection):
    """handels the conversion from image collection to a geopandas dataframe
    assumes that some level of pre processing has been done i.e. filering by bounds and dates
    """
    features = collection.toList(collection.size()).map(img2feat)
    fc = ee.FeatureCollection(features)

    # convert json output from fc to dataframe
    geojson = fc.getInfo()

    # call class constructor for GeoDataFrame.features
    gdf = gpd.GeoDataFrame.from_features(geojson["features"])

    # handles if there is no projection info
    if gdf.crs is None:
        gdf.set_crs(4326, inplace=True)

    # handles if the projection info is not wgs84
    if gdf.crs != 4326:
        gdf.to_crs(4326, inplace=True)

    # re arange the column names
    column_names = gdf.columns.tolist()
    if column_names[-1] != "geometry":
        geom = column_names.pop(column_names.index("geometry"))
        column_names.insert(len(column_names), geom)

    return gdf[column_names]
