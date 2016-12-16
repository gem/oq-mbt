import os
import unittest
import numpy

from mbt.importers.faults import get_oq_shp_faults
from mbt.utils import get_lons_lats_from_line

class TestFaultImport(unittest.TestCase):

    def test_import_oq(self):
        # Read the shapefile
        path = './data/shapefiles/oq/simple_fault_simple.shp'
        filename = os.path.join(os.path.dirname(__file__), path)
        srclist = get_oq_shp_faults(filename)
        # Check the content of the source list
        self.assertEqual(len(srclist), 1)
        # Check source
        src = srclist[0]
        self.assertEqual(src.source_id, 'sf3')
        lons, lats = get_lons_lats_from_line(src.trace)
        # Check longitudes
        expected = numpy.array([1.0, 1.4, 1.7])
 	numpy.testing.assert_array_equal(numpy.array(lons), expected) 
        # Check latitudes
        expected = numpy.array([-0.2, 0.0, 0.0])
 	numpy.testing.assert_array_equal(numpy.array(lats), expected) 
        # Check dip
        self.assertEqual(30., src.dip)
        # Check rake
        self.assertEqual(90., src.rake)
        # Check depths
        self.assertEqual(5., src.upper_depth)
        self.assertEqual(15., src.lower_depth)
        # Magnitude-scaling relationship
        print src.magnitude_scaling_relationship
        self.assertEqual('WC1994', src.magnitude_scaling_relationship)

    def test_import_fmg(self):
        # Read the shapefile
        path = './data/shapefiles/oq/simple_fault_simple.shp'
        filename = os.path.join(os.path.dirname(__file__), path)
        srclist = get_oq_shp_faults(filename)
        # Check the content of the source list
        self.assertEqual(len(srclist), 1)
        # Check source
        src = srclist[0]
        self.assertEqual(src.source_id, 'sf3')
        lons, lats = get_lons_lats_from_line(src.trace)
        # Check longitudes
        expected = numpy.array([1.0, 1.4, 1.7])
 	numpy.testing.assert_array_equal(numpy.array(lons), expected) 
        # Check latitudes
        expected = numpy.array([-0.2, 0.0, 0.0])
 	numpy.testing.assert_array_equal(numpy.array(lats), expected) 
