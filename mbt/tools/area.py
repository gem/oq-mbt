import numpy

from copy import deepcopy

from prettytable import PrettyTable

from hmtk.seismicity.selector import CatalogueSelector
from hmtk.sources.area_source import mtkAreaSource

from mbt.sources import OQtSource

from openquake.hazardlib.geo.polygon import Polygon

def src_oqt_to_hmtk(src):
    return mtkAreaSource(
            identifier=src.source_id, 
            name=src.name, 
            geometry=src.polygon)

def create_catalogue(sources, catalogue, polygon=None, print_log=False):
    """
    Note that this assumes that the catalogue has a rtree spatial index
    associated.
    
    :parameter sources:
	A list of sources
    :parameter catalogue:
        An instance of the hmtk catalogue
    :parameter polygon:
        An instance of the :class:'openquake.hazardlib.geo.polygon.Polygon' 
    """
    
    if len(sources) is not None:
        # Check input
        if len(sources) > 1: 
            raise ValueError('We do not support the analyses of more than one source') 
    	# Process the area sources
        src = sources[0]
	src_id = src.source_id
	# Check if the area source has a geometry
	if 'polygon' in src.__dict__:
	    pass
#	elif src_id in model.nrml_sources:
#            src.polygon = model.nrml_sources[src_id].polygon
#            src.name = model.nrml_sources[src_id].name
#            src.source_id = model.nrml_sources[src_id].source_id
	else: 
	    print 'The source does not have a geometry assigned'
	    return None
    elif polygon is not None:
	    assert isinstance(polygon, Polygon)
	    src_id = 'user_defined'
	    src = OQtSource('id', 'AreaSource')
	    src.name = 'dummy'
	    src.polygon = polygon
    else:
	    msg = 'Either a polygon or a list of sources must be defined'
	    raise ValueError(msg)
 
    # This sets the limits of the area covered by the polygon
    limits = [numpy.min(src.polygon.lons),
              numpy.min(src.polygon.lats),
              numpy.max(src.polygon.lons),
              numpy.max(src.polygon.lats)]
    # Src hmtk
    src_hmtk = src_oqt_to_hmtk(src)
    # This creates a new catalogue with eqks within the bounding box of 
    # the analysed area source
    selectorB = CatalogueSelector(catalogue, create_copy=True)
    tmpcat = selectorB.within_bounding_box(limits)
    selectorA = CatalogueSelector(tmpcat, create_copy=False)
    # This filters out the eqks outside the area source
    src_hmtk.select_catalogue(selectorA)
    # Create the composite catalogue as a copy of the sub-catalogue for the first source
    labels = ['%s' % src_id for i in range(0, len(src_hmtk.catalogue.data['magnitude']))]
    src_hmtk.catalogue.data['comment'] = labels
    fcatal = deepcopy(src_hmtk.catalogue)
    if print_log:
        print '# eqks for source', src_id, ':', len(src_hmtk.catalogue.data['magnitude'])
    # Complete the composite subcatalogue
    """
    for src_id in area_source_ids_list[1:]:
        # Set the source index and fix the catalogue selector
        src = model.sources[src_id]
        src_hmtk = src_oqt_to_hmtk(src)
        # Merge the source-subcatalogue to the composite one
        # print 'merging eqks for source:', src_id, '# eqks:', len(src_hmtk.catalogue.data['magnitude'])
        labels = ['%s' % src_id for i in range(0, len(src_hmtk.catalogue.data['magnitude']))]
        src_hmtk.catalogue.data['comment'] = labels
        fcatal.concatenate(src.catalogue)
    """
    if print_log:
        print 'Total number of earthquakes selected ', fcatal.get_number_events()
    return fcatal


def create_gr_table(model):
	# Set table
	p = PrettyTable(["ID","a_gr", "b_gr"])
	p.align["Source ID"] = 'l'
	p.align["a_gr"] = 'r'
	p.align["b_gr"] = 'r'
	#
	for key in sorted(model.sources):
	    src = model.sources[key]
	    if src.source_type == 'AreaSource':
	        alab = ''
	        blab = ''
	        if src.__dict__.has_key('a_gr'):
	            alab = '%8.5f' % (src.a_gr)
	        if src.__dict__.has_key('b_gr'):
	            blab = '%6.3f' % (src.b_gr)    
	        p.add_row([key, alab, blab])
	return p
	
def create_mmax_table(model):
	# Set table
	p = PrettyTable(["ID","mmax obs", "mmax assigned", "mo strain"])
	p.align["Source ID"] = 'l'
	p.align["mmax obs"] = 'r'
	p.align["mmax assigned"] = 'r'
	p.align["mo strain"] = 'r'
	#
	for key in sorted(model.sources):
	    src = model.sources[key]
	    if src.source_type == 'AreaSource':
	        alab = ''
	        blab = ''
	        clab = ''
	        if src.__dict__.has_key('mmax_obs'):
	            alab = '%6.2f' % (src.mmax_obs)
	        if src.__dict__.has_key('mmax_expected'):
	            blab = '%6.2f' % (src.mmax_expected)
	        if src.__dict__.has_key('mo_strain'):
	            clab = '%6.2e' % (src.mo_strain)     
	        p.add_row([key, alab, blab, clab])
	return p

def plot_area_source_polygons(model, bmap):
	"""
	:parameter bmap:
		A :class:Basemap instance
	"""
	for key in sorted(model.sources):
	    src = model.sources[key]
	    if src.source_type == 'AreaSource':
			x, y = bmap(src.polygon.lons, src.polygon.lats)
			bmap.plot(x, y, '-b')
