
import math
import numpy
from openquake.hazardlib.geo.mesh import Mesh

def _get_rate_above_m_low(seismic_moment, m_low, m_upp, b_gr=1.0):
    """
    :parameter seismic_moment:
        Seismic moment in Nm
    :parameter m_low:
        Lower magnitude threshold
    :parameter m_upp:
        Upper magnitude threshold
    :parameter b_gr:
        b value of the Gutenberg-Richter relationship
    """
    a_m = 9.1
    b_m = 1.5
    beta = b_gr * numpy.log(10.)
    x = (-seismic_moment*(b_m*numpy.log(10.) - beta) /
         (beta*(10**(a_m + b_m*m_low) -
          10**(a_m + b_m*m_upp)*numpy.exp(beta*(m_low - m_upp)))))
    rate_m_low = x * (1-numpy.exp(-beta*(m_upp-m_low)))
    return rate_m_low


def _get_cumul_rate_truncated(m, m_low, m_upp, rate_gt_m_low, b_gr=1.0):
    """
    This is basically equation 9 of Youngs and Coppersmith (1985)
    """
    beta = b_gr * numpy.log(10.)
    nmr1 = numpy.exp(-beta*(m-m_low))
    nmr2 = numpy.exp(-beta*(m_upp-m_low))
    den1 = 1-numpy.exp(-beta*(m_upp-m_low))
    rate = rate_gt_m_low * (nmr1 - nmr2) / den1
    return rate


def rates_for_double_truncated_mfd(area, slip_rate, m_low, m_upp,
                                   b_gr, bin_width=0.1):
    """
    :parameter area:
        Area of the fault surface
        float [km2]
    :parameter slip_rate:
        Slip-rate
        float [mm/tr]
    :parameter m_low:
        Lower magnitude
        float
    :parameter m_upp:
        Upper magnitude
    :parameter bin_width:
        Bin width
    :parameter b_gr:
        b-value of Gutenber-Richter relationship
    :return:
        A list containing the rates per bin starting from m_low
    """

    rigidity_Pa = 32 * 1e9  # [GPa] -> [Pa]

    # Compute moment
    slip_m = slip_rate * 1e-3  # [mm/yr] -> [m/yr]
    area_m2 = area * 1e6
    moment_from_slip = (rigidity_Pa * area_m2 * slip_m)

    # Compute total rate
    rate_above = _get_rate_above_m_low(moment_from_slip, m_low, m_upp)

    # Compute rate per bin
    rrr = []
    mma = []
    for mmm in numpy.arange(m_low, m_upp, bin_width):
        rte = (_get_cumul_rate_truncated(mmm, m_low, m_upp, rate_above, b_gr) -
               _get_cumul_rate_truncated(mmm+bin_width, m_low,
                                         m_upp, rate_above, b_gr))
        mma.append(mmm+bin_width/2)
        rrr.append(rte)
    return rrr
