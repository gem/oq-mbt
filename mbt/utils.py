""" Module utils contains simple utility functions used in different
components of the project"""

import numpy
from openquake.hazardlib.geo.point import Point


def get_source_list(trt_models):
    """
    Get the list of sources included in a
    :class:`openquake.commonlib.TRT_model`
    """
    sources = []
    for trtm in trt_models:
        sources += trtm.sources
    return sources


def mag_to_mo(mag):
    """
    Scalar moment [in Nm] from moment magnitude

    :return:
        The computed scalar seismic moment
    """
    return 10**(1.5*mag+9.0)


def mo_to_mag(mo):
    """
    From moment magnitude to scalar moment [in Nm]

    :return:
        The computed magnitude
    """
    return (numpy.log10(mo)-9.0)/1.5


def get_point_list(lons, lats):
    """
    :returns:
        Returns a list of :class:` openquake.hazardlib.geo.point.Point`
        instances
    """
    points = []
    for i in range(0, len(lons)):
        points.append(Point(lons[i], lats[i]))
    return points


class GetSourceIDs(object):

    def __init__(self, model):
        self.model = model
        self.reset()

    def reset(self):
        self.keys = set([key for key in self.model.sources])

    def keep_equal_to(self, param_name, values):
        """
        :parameter str param_name:
        :parameter list values:
        """
        assert type(values) is list
        tmp = []
        for key in self.keys:
            src = self.model.sources[key]
            param_value = getattr(src, param_name)
            for value in values:
                if param_value == value:
                    tmp.append(key)
                    continue
        self.keys = tmp

    def keep_gt_than(self, param_name, value):
        tmp = []
        for key in self.keys:
            src = self.model.sources[key]
            param_value = getattr(src, param_name)
            if param_value > value:
                tmp.append(key)
        self.keys = tmp

    def keep_lw_than(self, param_name, value):
        tmp = []
        for key in self.keys:
            src = self.model.sources[key]
            param_value = getattr(src, param_name)
            if param_value < value:
                tmp.append(key)
        self.keys = tmp
