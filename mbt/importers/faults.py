
import os
import re

from osgeo import ogr
from shapely import wkt

from mbt.sources import OQtSource
from mbt.utils import get_point_list

from openquake.hazardlib.geo.line import Line

MAPPING_OQ = {'identifier': 'id',
              'name': 'name',
              'tectonic_region_type': 'trt',
              'magnitude_scaling_relationship': 'msr',
              'rupture_aspect_ratio': 'rar',
              'rake': 'rake',
			  'upper_depth': 'usd',
			  'lower_depth': 'lsd',
              'rupture_aspect_ratio' : 'rar',
              'dip': 'dip',
             }

MAPPING_FMG = {'identifier': 'ID',
               'name': 'NAME',
               'dip': 'DIP',
               'rake': 'RAKE',
               'upper_depth': 'DMIN',
               'lower_depth': 'DMAX',
               'recurrence': 'RECURRENCE',
               'slip_rate': 'Sliprate',
               'aseismic': 'COEF',
               'mmax': 'MMAX',
               'ri': 'RECURRENCE',
               'coeff_fault': 'COEF'
              }


def get_oq_shp_faults(shapefile_filename, mapping=None, log=False):
    """
    Creates al list of OQtSource istances starting from a shapefile
    
    :returns:
		A list of :class:OQtSource instances   
	"""
    # set the default mapping
    if mapping is None:
        mapping = MAPPING_OQ	
    # check if file exists
    assert os.path.exists(shapefile_filename)
    # reading the file
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(shapefile_filename, 0)
    layer = dataSource.GetLayer()
    # reading sources geometry
    sources = []
    sources_data = {}
    for cnt, feature in enumerate(layer):
        # get dip
        dip = float(feature.GetField(mapping['dip']))
        # get geometry
        geom = feature.GetGeometryRef()
        geom_wkt = geom.ExportToWkt()
        if re.search('^MULTILINESTRING', geom_wkt):
            print 'skipping'
            print '   ', feature.GetField(mapping['name'])
        else:
            line = wkt.loads(geom.ExportToWkt())
            x, y = line.coords.xy
            # Check dip value
            if dip > 90 or dip < 0:
                print 'dip outside admitted range'
                print '   ', feature.GetField(mapping['dip'])
                print '   ', feature.GetField(mapping['name'])
            # Get fault ID and set internal ID
            tmp = feature.GetField(mapping['identifier'])
            if isinstance(tmp, str):
                sid = 'sf'+tmp
            elif isinstance(tmp, int):
                sid = 'sf%d' % tmp
            elif isinstance(tmp, float):
				sid = 'sf%d' % (int(tmp))
            else:
                raise ValueError('Unsupported ID type')

            src = OQtSource(sid, 'SimpleFaultSource')
            src.trace = Line(get_point_list(x, y))
            
            src.dip = float(feature.GetField(mapping['dip']))
            src.upper_depth = float(feature.GetField(mapping['upper_depth']))
            src.lower_depth = float(feature.GetField(mapping['lower_depth']))
            src.magnitude_scaling_relationship = feature.GetField(mapping['magnitude_scaling_relationship'])
            #src.name = feature.GetField(mapping['name'])
            src.rake = float(feature.GetField(mapping['rake']))
            #src.mmax = float(feature.GetField(mapping['mmax']))
            #src.ri = float(feature.GetField(mapping['ri']))
            #src.coeff = float(feature.GetField(mapping['coeff_fault']))
            
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
    sources_data = {}
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

            print sid,
            print 'name:', feature.GetField(mapping['name']),
            print 'dip:', feature.GetField(mapping['dip'])

            src = OQtSource(sid, 'SimpleFaultSource')
            src.trace = Line(get_point_list(x, y))
            src.dip = float(feature.GetField(mapping['dip']))
            src.upper_depth = float(feature.GetField(mapping['upper_depth']))
            src.lower_depth = float(feature.GetField(mapping['lower_depth']))
            src.name = feature.GetField(mapping['name'])
            src.slip_rate = float(feature.GetField(mapping['slip_rate']))
            src.recurrence = float(feature.GetField(mapping['recurrence']))
            src.rake = float(feature.GetField(mapping['rake']))
            src.mmax = float(feature.GetField(mapping['mmax']))
            src.ri = float(feature.GetField(mapping['ri']))
            src.coeff = float(feature.GetField(mapping['coeff_fault']))
            sources.append(src)
    dataSource.Destroy()

    srtd = sorted(sources, key=lambda x: x.source_id, reverse=False)
    if log:
        for src in srtd:
            print '%4s %-40s' % (src.id, src.name)
    return srtd, sources_data
