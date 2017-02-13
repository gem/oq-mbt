Modules 
=======

Shallow fault sources 
---------------------

Set the MFD
^^^^^^^^^^^

:Name: double_truncated_mfd_from_sliprate
:Long: With this 

- m_low         Lowest magnitude
- bin_width     Width of the bins used to describe the discrete MFD
- scalerel_name Scaling relationship name (as in the oq-hazardlib)

Example of config parameters:
``params={'m_low': 6.5, 'bin_width': 0.1, 'scalerel_name': 'WC1994'}``

