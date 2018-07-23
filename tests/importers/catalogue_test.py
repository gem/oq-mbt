import os
import unittest
# import numpy

from mbt.importers.catalogues import get_hmtk_catalogue


class TestCatalogueImport(unittest.TestCase):

    def test_import_hmtk(self):
        # Read the catalogue
        path = './data/catalogue/sample_catalogue.csv'
        filename = os.path.join(os.path.dirname(__file__), path)
        cat = get_hmtk_catalogue(filename)
        # Check the content of the source list
        self.assertEqual(len(cat.data['magnitude']), 19)
        #
        self.assertEqual(cat.data['magnitude'][0], 7.69)
        self.assertEqual(cat.data['year'][0], 1902)
        self.assertEqual(cat.data['month'][0], 8)
        #
        self.assertEqual(cat.data['depth'][1], 20.)
