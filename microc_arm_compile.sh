#!/bin/bash

# argument $1 has the microC filename in ./sample_codes

cd "./sample_codes"

# generate the llvm code
clang -S -emit-llvm -O0 -fno-discard-value-names "$1.c" -o "$1.ll"

# generate mlir llvm dialect
mlir-translate-20 --import-llvm --mlir-print-op-generic "$1.ll" -o "$1.mlir"

cd ".."

# run the python code
python "xdsl_microc.py" "$1"