#!/bin/bash
export PYTHONPATH=../model_building_tools:../hmtk:../oq-nrmllib:../oq-hazardlib:../oq-engine:../oq-mbt:
# add --no-browser to skip
jupyter-notebook $*