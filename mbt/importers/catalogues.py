from hmtk.parsers.catalogue.csv_catalogue_parser import CsvCatalogueParser

def get_hmtk_catalogue(filename):
    catalogue_parser = CsvCatalogueParser(filename)
    return catalogue_parser.read_file()
