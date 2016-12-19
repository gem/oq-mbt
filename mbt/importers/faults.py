
import os
import re

from osgeo import ogr
from shapely import wkt

from mbt.sources import OQtSource
from mbt.utils import get_point_list

from openquake.hazardlib.geo.line import Line

TYPES = {
         'a_val': 'float',
         'b_val': 'float',
         'dip': 'float',
         'identifier': 'str',
         'lower_depth': 'float',
         'magnitude_scaling_relationship': 'str',
         'max_mag': 'float',
         'min_mag': 'float',
         'name': 'str',
         'rupture_aspect_ratio': 'float',
         'rake': 'float',
         'tectonic_region_type': 'str',
         'upper_depth': 'float',
         'rupture_aspect_ratio' : 'float',
        }

for idx in range(0,6):
    TYPES['hd%d' % (idx)] = 'float'
    TYPES['hdweight%d' % (idx)] = 'float'

for idx in range(0,6):
    TYPES['dip%d' % (idx)] = 'float'
    TYPES['rake%d' % (idx)] = 'float'
    TYPES['strike%d' % (idx)] = 'float'
    TYPES['npweight%d' % (idx)] = 'float'

MAPPING_OQ = {
              'a_val': 'a_val',
              'b_val': 'b_val',
              'id': 'identifier',
              'name': 'name',
              'trt': 'tectonic_region_type',
              'max_mag': 'max_mag',
              'min_mag': 'min_mag',
              'msr': 'magnitude_scaling_relationship',
              'rar': 'rupture_aspect_ratio',
              'rake': 'rake',
	      'usd': 'upper_depth',
	      'lsd': 'lower_depth',
              'dip': 'dip',
             }

for idx in range(0,6):
    MAPPING_OQ['hd%d' % (idx)] = 'hd%d' % (idx)
    MAPPING_OQ['hdweight%d' % (idx)] = 'hdweight%d' % (idx)

for idx in range(0,6):
    MAPPING_OQ['dip%d' % (idx)] = 'dip%d' % (idx)
    MAPPING_OQ['rake%d' % (idx)] = 'rake%d' % (idx)
    MAPPING_OQ['strike%d' % (idx)] = 'strike%d' % (idx)
    MAPPING_OQ['npweight%d' % (idx)] = 'npweight%d' % (idx)

MAPPING_FMG = {'identifier': 'ID',
               'name': 'NAME',
               'dip': 'DIP',
               'rake': 'RAKE',
               'upper_depth': 'DMIN',
               'lower_depth': 'DMAX',
               'recurrence': 'RECURRENCE',
               'slip_rate': 'Sliprate',
               'slip_max': 'Slip_Max',
               'slip_min': 'Slip_Min',
               'aseismic': 'COEF',
               'mmax': 'MMAX',
               'ri': 'RECURRENCE',
               'ccoeff': 'COEF'
              }


def get_value(key, value):
    """
    Convert an attribute string to the corresponding value
        :param key:
        :param value:
        :return:
    """
    if TYPES[key] == 'str':
        return value
    elif TYPES[key] == 'float':
        value = float(value)
        # Check dip value
        if key == 'dip':
            if value > 90 or value < 0:
                print 'dip outside admitted range'
        return value
    elif TYPES[key] == 'int':
        return int(value)	    
    else:
        raise ValueError('Unknown type')
	

def get_oq_shp_faults(shapefile_filename, log=False):
    """
    Creates al list of OQtSource istances starting from a shapefile
    :value shapefile_filename:
    :returns:
        A list of :class:OQtSource instances   
    """
    # set the default mapping
    mapping = MAPPING_OQ
    admitted = set()
    for key in TYPES:
        admitted.add(key)
    print 'Admitted:', admitted
                                    
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
        print fieldName
        if fieldName in mapping and mapping[fieldName] in admitted:
            fieldnames.add(fieldName)
    
    # reading sources geometry
    sources = []
    for cnt, feature in enumerate(layer):
		
        # Get geometry
        geom = feature.GetGeometryRef()
        geom_wkt = geom.ExportToWkt()
        if re.search('^MULTILINESTRING', geom_wkt):
            print 'multilinestring skipping'
            print '   ', feature.GetField('name')
            continue
        else:
            line = wkt.loads(geom.ExportToWkt())
            x, y = line.coords.xy 

        # Get fault ID and set internal ID
        tmp = feature.GetField('id')
        if isinstance(tmp, str):
            sid = 'sf'+tmp
        elif isinstance(tmp, int):
            sid = 'sf%d' % tmp
        elif isinstance(tmp, float):
            d = 'sf%d' % (int(tmp))
        else:
            raise ValueError('Unsupported ID type')
		
	# Create a new source and set the geometry
        src = OQtSource(sid, 'SimpleFaultSource')
        src.trace = Line(get_point_list(x, y))
		
	# Get attributes
        for key in fieldnames:
	    value = get_value(mapping[key], feature.GetField(key))
            setattr(src, mapping[key], value)

        sources.append(src)
    dataSource.Destroy()

    srtd = sorted(sources, key=lambda x: x.source_id, reverse=False)
    if log:
        for src in srtd:
            print '%4s %-40s' % (src.id, src.name)
    return srtd

def get_fmg_faults(shapefile_filename, mapping=None, log=False):
    """
    Creates al list of OQtSource istances starting from a shapefile

    :parameter string shapefile_filename:
        Name of the shapefile containing information on active faults
    :parameter mapping:
        A dictionary indicating for each parameter in the shapefile 
        attribute table the corresponding one in the mtkActiveFault 
        object. Note that only the information listed in this
        dictionary will be included in the OQtSource istances.
    """
    # set the default mapping. This is based on the information in the
    # attribute table of the shapefile Yufang sent in Sept. 2015.
    if mapping is None:
        mapping = MAPPING_FMG
    # check if file exists
    assert os.path.exists(shapefile_filename)
    # reading the file
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(shapefile_filename, 0)
    layer = dataSource.GetLayer()
    # reading sources geometry
    sources = []
    for cnt, feature in enumerate(layer):
        # get dip
        dip = float(feature.GetField(mapping['dip']))
        # get geometry
        geom = feature.GetGeometryRef()
        geom_wkt = geom.ExportToWkt()
        if (re.search('^MULTILINESTRING', geom_wkt) or dip < 0.1 or
                feature.GetField("TYPE") == 'SUB'):
            print 'skipping'
            print '   ', feature.GetField(mapping['name'])
        else:
            line = wkt.loads(geom.ExportToWkt())
            x, y = line.coords.xy
            if dip > 90 or dip < 0:
                print 'dip outside admitted range'
                print '   ', feature.GetField(mapping['dip'])
                print '   ', feature.GetField(mapping['name'])

            tmp = feature.GetField(mapping['identifier'])
            if isinstance(tmp, str):
                sid = 'sf'+tmp
            elif isinstance(tmp, int):
                sid = 'sf%d' % tmp
            elif isinstance(tmp, float):
				sid = 'sf%d' % (int(tmp))
            else:
                raise ValueError('Unsupported ID type')
            # Read attributes
            src = OQtSource(sid, 'SimpleFaultSource')
            src.trace = Line(get_point_list(x, y))
            src.dip = float(feature.GetField(mapping['dip']))
            src.rake = float(feature.GetField(mapping['rake']))
            # seismogenic thickness
            src.upper_depth = float(feature.GetField(mapping['upper_depth']))
            src.lower_depth = float(feature.GetField(mapping['lower_depth']))
            src.name = feature.GetField(mapping['name'])
            # slip
            src.slip_rate = float(feature.GetField(mapping['slip_rate']))
            src.slip_max = float(feature.GetField(mapping['slip_max']))
            src.slip_min = float(feature.GetField(mapping['slip_min']))
            # recurrence
            src.recurrence = float(feature.GetField(mapping['recurrence']))
            src.mmax = float(feature.GetField(mapping['mmax']))
            src.ri = float(feature.GetField(mapping['ri']))
            # coupling coefficient
            src.ccoeff = float(feature.GetField(mapping['ccoeff']))
            sources.append(src)
    dataSource.Destroy()

    srtd = sorted(sources, key=lambda x: x.source_id, reverse=False)
    if log:
        for src in srtd:
            print '%4s %-40s' % (src.id, src.name)
    return srtd
