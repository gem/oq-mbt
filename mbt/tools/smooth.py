
import numpy
import rtree
import scipy.constants as consts

from mbt.tools.geo import get_idx_points_inside_polygon

from openquake.hazardlib.geo.geodetic import (point_at,
                                              min_geodetic_distance)


def coord_generators(mesh):
    for cnt, pnt in enumerate(mesh):
        lon = pnt.longitude
        lat = pnt.latitude
        yield (cnt, (lon, lat, lon, lat), 1)


class Smoothing:
    def __init__(self, catalogue, mesh, cellsize, completeness=None):
        self.catalogue = catalogue
        self.mesh = mesh
        self.cellsize = cellsize
        self.completeness = completeness
        self._create_spatial_index()

    def _create_spatial_index(self):
        # Setting properties
        p = rtree.index.Property()
        p.get_overwrite = True

        # Create the spatial index for the grid mesh
        r = rtree.index.Index('./tmp', properties=p)
        for cnt, pnt in enumerate(coord_generators(self.mesh)):
            r.insert(id=pnt[0], coordinates=pnt[1])

        # Create nodes array
        # MN: nodes is never used
        nodes = numpy.array((len(self.mesh)))

        self.rtree = r

    def gaussian(self, radius, sigma):
        # Values
        values = numpy.zeros((len(self.mesh)))
        # Compute the number of expected nodes
        # MN: numptns is never used
        numpnts = consts.pi*radius**2/(self.cellsize**2)
        # Smoothing the catalogue
        for lon, lat, mag in zip(self.catalogue.data['longitude'],
                                 self.catalogue.data['latitude'],
                                 self.catalogue.data['magnitude']):
            # set the bounding box
            minlon, minlat = point_at(lon, lat, 225, radius*2**0.5)
            maxlon, maxlat = point_at(lon, lat, 45, radius*2**0.5)
            # find nodes within the bounding box
            idxs = list(self.rtree.intersection((minlon,
                                                 minlat,
                                                 maxlon,
                                                 maxlat)))
            # get distances
            dsts = min_geodetic_distance(lon, lat,
                                         self.mesh.lons[idxs],
                                         self.mesh.lats[idxs])
            jjj = numpy.nonzero(dsts < 50)[0]
            idxs = numpy.array(idxs)
            iii = idxs[jjj]
            # set values
            tmpvalues = numpy.exp(-dsts[jjj]/sigma**2)
            normfact = sum(tmpvalues)
            values[iii] += tmpvalues/normfact
        return values

    def get_points_in_polygon(self, polygon):

        minlon = min(polygon.lons)
        minlat = min(polygon.lats)
        maxlon = max(polygon.lons)
        maxlat = max(polygon.lats)

        idxs = list(self.rtree.intersection((minlon, minlat,
                                             maxlon, maxlat)))
        plons = self.mesh.lons[idxs]
        plats = self.mesh.lats[idxs]

        iii = get_idx_points_inside_polygon(plon=plons,
                                            plat=plats,
                                            poly_lon=polygon.lons,
                                            poly_lat=polygon.lats,
                                            pnt_idxs=idxs,
                                            buff_distance=0.)

        return iii
