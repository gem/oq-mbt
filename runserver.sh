#!/bin/bash


usage () {
    echo
    echo "$0 - run jupyter-notebook with the right environmenti variables"
    echo
    echo "$0 [-r|--ref] [--no-browser]"
    echo "   -r|--ref      use repository paths for project and data directories"
    echo "   --no-browser  don't open new browser page"
    echo "   -h|--help     this help"
    echo
    exit $1
}
while [ $# -ne 0 ]
do
    arg="$1"
    case "$arg" in
        -r|--ref)
            reference="true"
            ;;
        -h|--help)
            usage 0
            ;;
        *)
            break
            ;;
    esac
    shift
done

export PYTHONPATH=$PWD/../model_building_tools:$PWD/../hmtk:$PWD/../oq-nrmllib:$PWD/../oq-hazardlib:$PWD/../oq-engine:$PWD:

if [ "$reference" = "true" ]; then
    SCRIPT_PATH="$(dirname "$0")"              # relative
    SCRIPT_PATH="$( ( cd "$SCRIPT_PATH" && pwd ) )"  # absolutized and normalized
    export OQ_MBT_HOME=$SCRIPT_PATH/ref
    export OQ_MBT_DATA=$SCRIPT_PATH/ref-data
fi
# add --no-browser to skip
jupyter-notebook $*
