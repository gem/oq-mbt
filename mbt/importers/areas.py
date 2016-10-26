from osgeo import ogr
from shapely import wkt

from oqmbt.oqt_project import OQtSource

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

def areas_to_oqt_sources(shapefile_filename, idname='IDZ'):
    """
    :parameter str shapefile_filename:
        Name of the shapefile containing the polygons
    :returns:
        A list of :class:`oqmbt.oqt_project.OQtSource` istances
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
        print type(feature.GetField(idname))
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
