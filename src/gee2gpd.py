import ee
import geopandas as gpd
import pandas as pd

from timezonefinder import TimezoneFinder


def img2feat(element: ee.Image) -> ee.feature.Feature:
    """converts image to feature"""
    data = ee.Image(element)
    # copy all properties from the src image to the dest feature
    geom = data.geometry()
    prop_names = data.propertyNames()
    props = data.toDictionary(prop_names)
    return ee.Feature(geom, props)


def localize_utc_time(df) -> gpd.GeoDataFrame:
    # date time conversion
    time = time or "system:time_start"
    tf = TimezoneFinder()
    df["timezone"] = df.apply(
        lambda x: tf.timezone_at(lng=x["x"], lat=x["y"]), axis=1
    )
    df["utc"] = df[time] / 1000.0
    df["timestamp"] = pd.to_datetime(df["utc"], unit="s")
    df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")
    df["timestamp"] = df.apply(
        lambda row: row["timestamp"].tz_convert(row["timezone"]), axis=1
    )
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df['date'] = df['timestamp'].dt.strftime('%Y-%m-%d')
    df["year"] = df["timestamp"].dt.year
    df['month'] = df["timestamp"].dt.month
    df['day'] = df["timestamp"].dt.day
    df["julian_date"] = df["timestamp"].dt.dayofyear
    return df


def gee2gpd(collection: ee.ImageCollection, dt_col: str = None):
    """ converts ee.ImageCollection to gpd.GeoDataFrame. """
    
    if collection.size().getInfo() >= 5000:
        raise ee.ee_exception.EEException("Too many Object try reducing")
    
    # convert image to collection to list and convert each element to a feature
    iclist = collection.toList(collection.size()).map(img2feat)
    fc = ee.FeatureCollection(iclist)
    
    # convert get info from server and access features
    geojson = fc.getInfo()
    
    gdf = gpd.GeoDataFrame.from_features(geojson['features'])
    
    # check if a crs has been set
    if gdf.crs is None:
        gdf.set_crs(4326, inplace=True)
    
    # add x,y of the centroid
    gdf['x'] = gdf.geometry.centroid.x
    gdf['y'] = gdf.geometry.centroid.y
    
    # want to add dt field to the dataframe
    gdf = localize_utc_time(gdf, dt_col)
    
    return gdf