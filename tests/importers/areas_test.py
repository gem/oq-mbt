import os
import unittest
# import numpy

from mbt.importers.areas import areas_to_oqt_sources
# from mbt.utils import get_lons_lats_from_line


class TestAreasImport(unittest.TestCase):

    def test_import_oq(self):
        # Read the shapefile
        path = './data/shapefiles/oq/area_source_area.shp'
        filename = os.path.join(os.path.dirname(__file__), path)
        srcdict = areas_to_oqt_sources(filename)
        # Check the content of the source list
        self.assertEqual(len(srcdict), 1)
        keys = srcdict.keys()
        # Check source
        src = srcdict[keys[0]]
        self.assertEqual(src.source_id, '1')
        # Check name
        self.assertEqual(src.name, 'Area Source')
        # Check minmum magnitude
        self.assertEqual(src.lower_depth, 10.)
        # TRT
        self.assertEqual('Active Shallow Crust', src.tectonic_region_type)
        # RAR
        self.assertEqual(1.0, src.rupture_aspect_ratio)
        # USD and LSD
        self.assertEqual(0.0, src.upper_depth)
        self.assertEqual(10.0, src.lower_depth)
        # min and max magnitude
        self.assertEqual(5.0, src.min_mag)
        self.assertEqual(6.5, src.max_mag)
        # a and b values
        self.assertEqual(4.5, src.a_val)
        self.assertEqual(1.0, src.b_val)
        # Magnitude-scaling relationship
        self.assertEqual('WC1994', src.magnitude_scaling_relationship)
        # Rupture mechanism
        self.assertEqual(90., src.dip1)
        # Hypocentral depth
        self.assertEqual(5., src.hd1)
