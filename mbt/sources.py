import inspect
import re
import openquake.hazardlib.source as oqsrc

# List of valid attributes for an area source
AREAS_ATTRIBUTES = set(['source_id',
                        'name',
                        'tectonic_region_type',
                        'mfd',
                        'rupture_mesh_spacing',
                        'magnitude_scaling_relationship',
                        'rupture_aspect_ratio',
                        'temporal_occurrence_model',
                        'upper_seismogenic_depth',
                        'lower_seismogenic_depth',
                        'nodal_plane_distribution',
                        'hypocenter_distribution',
                        'polygon',
                        'area_discretization'])

AREAS_ATTRIBUTES |= set(['gr_aval',
                         'gr_bval',
                         'source_type'])

# List of valid attributes for a simple source
SIMPLE_FAULT_ATTRIBUTES = set(['source_id',
                               'name',
                               'tectonic_region_type',
                               'mfd',
                               'rupture_mesh_spacing',
                               'magnitude_scaling_relationship',
                               'rupture_aspect_ratio',
                               'temporal_occurrence_model',
                               'upper_seismogenic_depth',
                               'lower_seismogenic_depth',
                               'fault_trace',
                               'dip',
                               'rake',
                               'hypo_list',
                               'sliprate'])
                               
SIMPLE_FAULT_ATTRIBUTES |= set(['gr_aval',
                                'gr_bval',
                                'dip',
                                'rake',
                                'hypo_list',
                                'slip_list'])

SIMPLE_FAULT_ATTRIBUTES |= set(['gr_aval',
                                'gr_bval',
                                'source_type'])

# This adds support for shapefiles created by the OpenQuake-engine
SIMPLE_FAULT_ATTRIBUTES |= set([''])

# Create the set of valid source types
SOURCE_TYPES = set()
for name, obj in inspect.getmembers(oqsrc):
    if inspect.isclass(obj):
        if not re.search('Rupture', name):
            SOURCE_TYPES.add(name)


class OQtSource(object):
    """
    A container for information necessary to build and/or characterise an
    earthquake source

    :parameter str source_id:
        The ID of the source
    :parameter str source_type:
        Source type i.e. Object name amongst the ones admitted in the
        OpenQuake Hazardlib.

    """
    def __init__(self, *args, **kwargs):
        # Checks
        if len(args):
            self.source_id = args[0]
            if len(args) > 1:
                self.source_type = args[1]
        if len(kwargs):
            self.__dict__.update(kwargs)
        # Check mandatory attributes: ID
        if 'source_id' not in self.__dict__:
            raise ValueError('Source must have an ID')
        elif not isinstance(self.source_id, str):
            raise ValueError('ID must be a string')
        # Check mandatory fields: SOURCE TYPE
        if 'source_type' not in self.__dict__:
            raise ValueError('Source must have a type')
        if self.source_type not in SOURCE_TYPES:
            raise ValueError('Unrecognized source type: %s' % self.source_type)
        if 'source_type' in self.__dict__:
            attribute_set = AREAS_ATTRIBUTES
        elif 'source_type' in self.__dict__:
            attribute_set = SIMPLE_FAULT_ATTRIBUTES
        else:
            raise ValueError('Unsupported source type')
        # Check attributes
        for key in self.__dict__:
            if key not in attribute_set:
                print('Attribute set', attribute_set)
                msg = 'Parameter %s not compatible with this source' % (key)
                raise ValueError(msg)

    def get_info(self):
        for key in self.__dict__:
            print('%30s:' % (key), getattr(self, key))
