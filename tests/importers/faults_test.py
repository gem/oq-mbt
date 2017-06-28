import os
import unittest
import numpy

from mbt.importers.faults import get_oq_shp_faults, get_fmg_faults
from mbt.utils import get_lons_lats_from_line

class TestFaultImport(unittest.TestCase):

    def test_import_oq_with_slip(self):
        # Read the shapefile
        path = './data/shapefiles/oq/simple_fault_simple_with_slip.shp'
        filename = os.path.join(os.path.dirname(__file__), path)
        srcdict = get_oq_shp_faults(filename)
        keys = list(srcdict.keys())
        # Check sliprate value
        src = srcdict[keys[0]]
        self.assertEqual(src.sliprate, 1.23)


    def test_import_oq(self):
        # Read the shapefile
        path = './data/shapefiles/oq/simple_fault_simple.shp'
        filename = os.path.join(os.path.dirname(__file__), path)
        srcdict = get_oq_shp_faults(filename)
        keys = list(srcdict.keys())
        # Check the content of the source list
        self.assertEqual(len(keys), 1)
        # Check source
        src = srcdict[keys[0]]
        self.assertEqual(src.source_id, 'sf3')
        # Check longitudes
        lons, lats = get_lons_lats_from_line(src.trace)
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
        self.assertEqual('WC1994', src.magnitude_scaling_relationship)


    def test_import_fmg(self):
        # Read the shapefile
        path = './data/shapefiles/fmg/sample_faults_fmg_format.shp'
        filename = os.path.join(os.path.dirname(__file__), path)
        srcdict = get_fmg_faults(filename)
        keys = srcdict.keys()
        # Check the content of the source list
        print (len(keys))
        self.assertEqual(len(keys), 7)
        # Check source
        src = srcdict['sf137']
        self.assertEqual(src.source_id, 'sf137')
        self.assertEqual(src.name, 'BB')
        # Check dip
        self.assertEqual(70., src.dip)
        # Check rake
        self.assertEqual(-30, src.rake)
        # Check slip
        self.assertEqual(2.6, src.slip_max)
        self.assertEqual(0.6, src.slip_min)
        # Check coupling coefficient
        self.assertEqual(1.0, src.ccoeff)
