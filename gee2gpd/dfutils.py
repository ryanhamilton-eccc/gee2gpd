import geopandas as gpd
import pandas as pd

from timezonefinder import TimezoneFinder


## UTC CONVERSTION UTILITY FUNCTIONS


def insert_centroid_xy(df: gpd.GeoDataFrame):
    df["x"] = df.geometry.centroid.x
    df["y"] = df.geometry.centroid.y
    return df


def insert_time_zone(df: gpd.GeoDataFrame):
    cols = df.columns.tolist()
    if "x" not in cols and "y" not in cols:
        raise ValueError("x,y coordinates of the centroid must be added")
    tf = TimezoneFinder()
    df["timezone"] = df.apply(lambda x: tf.timezone_at(lng=x["x"], lat=x["y"]), axis=1)
    return df


def convert_utc_time(df: gpd.GeoDataFrame, time_col: str) -> gpd.GeoDataFrame:
    """converts utc time to local time"""
    # date time conversion
    cols = df.columns.tolist()
    if "timezone" not in cols or time_col not in cols:
        raise ValueError

    df["utc"] = df[time_col] / 1000.0
    df["timestamp"] = pd.to_datetime(df["utc"], unit="s")
    df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")
    df["timestamp"] = df.apply(
        lambda row: row["timestamp"].tz_convert(row["timezone"]), axis=1
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["date"] = df["timestamp"].dt.strftime("%Y-%m-%d")
    df["year"] = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.month
    df["day"] = df["timestamp"].dt.day
    df["julian_date"] = df["timestamp"].dt.dayofyear
    return df


def localize_utc(df, time_col: str = None):
    time_col = time_col or "system:time_start"
    df = insert_centroid_xy(df)
    df = insert_time_zone(df)
    df = convert_utc_time(df, time_col)
    return df[
        [
            i
            for i in df.columns.tolist()
            if i not in ["timestamp", "utc", "timezone", "x", "y"]
        ]
    ]
