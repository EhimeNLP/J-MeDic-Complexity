#!/bin/bash

INPUT="../data/words/sample.csv"
OUTPUT="../output/output.csv"

python extract_gzip.py
python make_vec.py $INPUT
python concat_vec.py
python svm.py $INPUT $OUTPUT