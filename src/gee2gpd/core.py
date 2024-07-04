import ee


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
