import sys
import warnings


import click
import ee
import geopandas as gpd

from gee2gpd import convert, dfutils


warnings.filterwarnings("ignore")


def gdf_to_fc(filepath: str, driver: str):
    gdf = gpd.read_file(filepath, driver=driver)
    if gdf.crs != 4326:
        gdf.to_crs(4326, inplace=True)

    # if the len is greater than 1 get the first row maintain df
    if len(gdf) > 1:
        gdf = gdf.iloc[0:1]

    return ee.FeatureCollection(gdf.__geo_interface__)


def load_spatial_file(args: str):
    """anything with a .shp or .geojson is treated as a spatial file anything else is assumed to be an asset id for gee file system"""
    if args.endswith(".shp"):
        return gdf_to_fc(args, driver="ESRI Shapefile").geometry()
    if args.endswith(".geojson"):
        return gdf_to_fc(args, driver="GeoJSON").geometry()
    return ee.FeatureCollection(args).first().geometry()


@click.command()
@click.option("--id", prompt="EE Image Collection ID")
@click.option("--start", prompt="Start Date", help="YYYY-MM-dd or YYYY")
@click.option("--end", prompt="End Date", help="YYYY-MM-dd or YYYY")
@click.option(
    "--aoi", prompt="Aoi file", help="asset id or path to shapefile or geojson"
)
def main(id, start, end, aoi):
    aoi = load_spatial_file(aoi)
    collection = ee.ImageCollection(id).filterBounds(aoi).filterDate(start, end)

    # convert collection
    gdf = convert.ic_to_dataframe(collection)

    # localize the date and time
    gdf = dfutils.localize_utc(gdf)

    # save the gdf to geojson
    file_name = ("_").join(id.split("/"))
    gdf.to_file(f"{file_name}.geojson", driver="GeoJSON")
    return 0


if __name__ == "__main__":
    sys.exit(main())
