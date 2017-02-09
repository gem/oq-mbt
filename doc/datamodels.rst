Configuration parameters
------------------------

Default catalogue processing parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Below we provide a list of parameters the user can specify for each model:

* `catalogue_cutoff_magnitude` - The value of magnitiude below which eartquakes included in the catalogue are discarded
* `catalogue_cutoff_depth` - The value of depth [km] below which eartquakes included in the catalogue are discarded


Default area source parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default shallow fault parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Below we provide a list of default parameters the user can specify for each model:

* `sfs_default_b_gr` - Gutenberg-Richter relationship b-value 
* `sfs_default_creeping_coefficient` - Fault creeping coefficient [0-1]. When equal to unity all the slip on the fault is considered aseismic.
* `sfs_default_lower_seismogenic_depth` - Lower seismogenic depth [km]
* `sfs_default_mesh_spacing` - Spacing of the mesh used to represent the fault surface [km]
* `sfs_default_mmin` - Minimum magnitude used - when necessary - to define the magnitude-frequency distribution for shallow fault sources
* `sfs_default_scalerel` - Name of the OpenQuake-engine magnitude scaling relationship class e.g. 'WC1994'
* `sfs_default_upper_seismogenic_depth` - Upper seismogenic depth [km]

Internal Data models
--------------------

Area sources
^^^^^^^^^^^^
An area source instance can have the following attributes:

* `id`
* `name`

Shallow Faults
^^^^^^^^^^^^^^

A fault instance can have the following attributes:

* `dip`
* `dipdir`
* `rake`
* `sliprate`

Subduction interface faults
^^^^^^^^^^^^^^^^^^^^^^^^^^^


