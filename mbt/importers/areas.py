import re
from osgeo import ogr
from shapely import wkt

# IDS and NAME are mandatory, everything else optional
PARAMETERS = {'IDS': str, 'NAME': str, 'MMAX': float, 'TRT': str}

def areas_to_oqt_sources(shapefile_filename):
    """
    :parameter str shapefile_filename:
        Name of the shapefile containing the polygons
    :returns:
        A list of :class:`oqmbt.oqt_project.OQtSource` istances
    """
    idname = 'Id'
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
        else:
            raise ValueError('Unsupported source ID type')
        # Create the source
        src = OQtSource(source_id=id_str,
                        source_type='AreaSource',
                        polygon=Polygon(points),
                        name=id_str)
        # Set tectonic region
        if feature.GetField('TRT')
			trt = _set_trt(feature.GetField('TRT'))
        # Append the new source
        if not id_set and set(id_str):
            sources[id_str] = src
        else:
            raise ValueError('Sources with non unique ID %s' % id_str)

    dataSource.Destroy()
    return sources
