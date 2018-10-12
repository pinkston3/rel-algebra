#!/bin/bash


PYTHON_GEN=./python_gen
JAVASCRIPT_GEN=./javascript_gen


rm -rf $PYTHON_GEN $JAVASCRIPT_GEN


java -jar antlr-4.7-complete.jar RelationalAlgebra.g4 -o $PYTHON_GEN \
	-Dlanguage=Python3 -listener -visitor

java -jar antlr-4.7-complete.jar RelationalAlgebra.g4 -o $JAVASCRIPT_GEN \
	-Dlanguage=JavaScript -listener -visitor


