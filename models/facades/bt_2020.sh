#!/usr/bin/env bash

# Uses the full year's worth of data

eval "$(conda shell.bash hook)";
conda activate mm22;
python $(dirname "$0")/bt_2020.py $1 $2 $3
