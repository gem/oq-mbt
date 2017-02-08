All about file formats and data models
======================================

File formats
------------

For specific information on shapefiles see https://en.wikipedia.org/wiki/Shapefile

Area sources
^^^^^^^^^^^^

Area sources can be produced starting from the information included in a shapefile.

Catalogues
^^^^^^^^^^

The MBT can read standard `.csv` earthquake catalogue files supported by the 
Hazard Modeller's Toolkit (see the oq-hmtk for additional information).

Shallow Faults
^^^^^^^^^^^^^^

The construction of fault sources with the oq-mbt starts from the information
included in a shapefile  

Strain rate
^^^^^^^^^^^

Strain rate models can be used for the characterisation of earthquake 
occurrence in the oq-mbt.

Internal Data models
--------------------

Shallow Faults
^^^^^^^^^^^^^^

In the oq-mbt, a fault instance can have the following attributes:

* `dip`
* `dipdir`
* `rake`
* `sliprate`


Area sources
^^^^^^^^^^^^
