import os

from osgeo import ogr
from shapely import wkt

from mbt.sources import OQtSource
from mbt.importers.faults import get_value, TYPES, MAPPING_OQ

from openquake.hazardlib.geo.polygon import Polygon
from openquake.hazardlib.geo.point import Point


def _get_point_list(lons, lats):
    """
    :returns:
        Returns a list of :class:` openquake.hazardlib.geo.point.Point`
        instances
    """
    points = []
    for i in range(0, len(lons)):
        points.append(Point(lons[i], lats[i]))
    return points


def areas_to_oqt_sources(shapefile_filename):
    """
    :parameter str shapefile_filename:
        Name of the shapefile containing the polygons
    :returns:
        A list of :class:`mbt.sources.OQtSource` istances
    """
    # set the default mapping
    mapping = MAPPING_OQ
    admitted = set()
    for key in TYPES:
        admitted.add(key)

    # check if file exists
    assert os.path.exists(shapefile_filename)

    # Reading the file
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(shapefile_filename, 0)
    layer = dataSource.GetLayer()
    layerDefinition = layer.GetLayerDefn()

    # Attribute table: get fields and selected the ones admitted
    fieldnames = set()
    for i in range(layerDefinition.GetFieldCount()):
        fieldName = layerDefinition.GetFieldDefn(i).GetName()
        if fieldName in mapping and mapping[fieldName] in admitted:
            fieldnames.add(fieldName)

    # reading sources geometry
    sources = {}
    id_set = set()
    for cnt, feature in enumerate(layer):

        # Get geometry
        geom = feature.GetGeometryRef()
        # geom_wkt = geom.ExportToWkt()

        # Read the geometry
        geom = feature.GetGeometryRef()
        polygon = wkt.loads(geom.ExportToWkt())
        x, y = polygon.exterior.coords.xy
        points = _get_point_list(x, y)

        # Set the ID
        idname = 'id'
        if isinstance(feature.GetField(idname), str):
            id_str = feature.GetField(idname)
        elif isinstance(feature.GetField(idname), int):
            id_str = '%d' % (feature.GetField(idname))
        else:
            raise ValueError('Unsupported source ID type')
        print('>>', id_str)

        # Create the source
        src = OQtSource(source_id=id_str,
                        source_type='AreaSource',
                        polygon=Polygon(points),
                        name=id_str)

        # Get attributes
        for key in fieldnames:
            value = get_value(mapping[key], feature.GetField(key))
            setattr(src, mapping[key], value)

        if not id_set & set([id_str]):
            sources[id_str] = src
            id_set.add(id_str)
        else:
            print(id_set)
            print(id_set & set(id_str))
            print('IDs:', id_str)
            raise ValueError('Sources with non unique ID %s' % id_str)

    dataSource.Destroy()
    return {key: sources[key] for key in sorted(sources)}

    """
    # Set the driver
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(shapefile_filename, 0)
    layer = dataSource.GetLayer()
    # Reading sources geometry
    sources = {}
    id_set = set()
    for feature in layer:
        # Read the geometry
        geom = feature.GetGeometryRef()
        polygon = wkt.loads(geom.ExportToWkt())
        x, y = polygon.exterior.coords.xy
        points = _get_point_list(x, y)
        # Set the ID
        if isinstance(feature.GetField(idname), str):
            id_str = feature.GetField(idname)
        elif isinstance(feature.GetField(idname), int):
            id_str = '%d' % (feature.GetField(idname))
        else:
            raise ValueError('Unsupported source ID type')
        # Create the source
        src = OQtSource(source_id=id_str,
                        source_type='AreaSource',
                        polygon=Polygon(points),
                        name=id_str)
        # Append the new source
        if not id_set and set(id_str):
            sources[id_str] = src
        else:
            raise ValueError('Sources with non unique ID %s' % id_str)

    dataSource.Destroy()
    return sources
    """
