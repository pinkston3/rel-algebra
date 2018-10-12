#!/bin/bash

APPDIR=ra2html

if [ -d $APPDIR ]; then
    echo "$APPDIR directory already exists"
    return
fi

mkdir $APPDIR

pip install -t $APPDIR antlr4-python3-runtime

cp python_gen/*.py $APPDIR
cp python/*.py $APPDIR
cp python/*.css $APPDIR

python -m zipapp $APPDIR -p '/usr/bin/env python3' -m ra2html_app:main

