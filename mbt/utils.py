
from openquake.hazardlib.geo.point import Point


def get_lons_lats_from_line(line):
    """
    """
    lons = []
    lats = []
    for pnt in (line.points):
        lons.append(pnt.longitude)
        lats.append(pnt.latitude)
    return (lons, lats)


def get_point_list(lons, lats):
    """
    :parameter lons:
    :parameter lats:
    	A :class:list of :class:openquake.hazardlib.geo.point.Point
    :returns:
        Returns a list of :class:` openquake.hazardlib.geo.point.Point`
        instances
    """
    points = []
    for i in range(0, len(lons)):
        points.append(Point(lons[i], lats[i]))
    return points
