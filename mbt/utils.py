
from openquake.hazardlib.geo.point import Point



def mag_to_mo(mag):
    """
    Scalar moment [in Nm] from moment magnitude

    :return:
        The computed scalar seismic moment
    """
    return 10**(1.5*mag+9.1)

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
        A list
    :parameter lats:
    	A list
    :returns:
        Returns a list of :class:` openquake.hazardlib.geo.point.Point`
        instances
    """
    points = []
    for i in range(0, len(lons)):
        points.append(Point(lons[i], lats[i]))
    return points
