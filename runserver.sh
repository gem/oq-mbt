#!/bin/bash
while [ $# -ne 0 ]
do
    arg="$1"
    case "$arg" in
        -r|--ref)
            reference="true"
            ;;
        *)
            ;;
    esac
    shift
done

export PYTHONPATH=../model_building_tools:../hmtk:../oq-nrmllib:../oq-hazardlib:../oq-engine
# add --no-browser to skip

if [ "$reference" = "true" ]; then
    SCRIPT_PATH="$(dirname "$0")"              # relative
    SCRIPT_PATH="$( ( cd "$SCRIPT_PATH" && pwd ) )"  # absolutized and normalized
    export OQ_MBT_HOME=$SCRIPT_PATH/ref
    export OQ_MBT_DATA=$SCRIPT_PATH/ref-data
fi
jupyter-notebook $*

