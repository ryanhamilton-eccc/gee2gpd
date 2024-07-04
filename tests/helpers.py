import ee


aoi = ee.Geometry.Point([-77.36492187600616, 44.170475135647266])
dates = ("2019-04-01", "2019-10-31")


def fetch_collection(id, aoi, dates: tuple[str, str]):
    return ee.ImageCollection(id).filterBounds(aoi).filterDate(*dates)


def fetch_l8sr_collection() -> ee.ImageCollection:
    return fetch_collection("LANDSAT/LC08/C02/T1_L2", aoi, dates)
