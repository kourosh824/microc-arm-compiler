# microc-arm-compiler
A basic compiler that takes C MLIR and compiles it to ARM assembly using xDSL.

## Prerequisites
1. We highly recommend working this project on Linux.
2. First you need to instal clang:
```bash
sudo apt install clang
```
3. You now have to install MLIR tools:
```bash
sudo apt-get install libmlir-20-dev mlir-20-tools
```
4. You must have Python installed on your system. While doing this project we used Python 3.13.5.
5. You now have to download the xDSL library for Python using pip:
```bash
pip install xdsl
```

## What is this compiler?
This compiler is made of a backend for compiling C code to ARM. The backend only supports some C operations and that is why we prefer to call it microC. We use clang to generate the LLVM file and then use MLIR tools to translate this LLVM file to MLIR's LLVM dialect. We then use xDSL to read this intermediate representation and compile the microC code to ARM.


## What does each file do?
| File Name      | Description |
| ----------- | ----------- |
| ```xdsl_llvm_operations.py```      | xDSL's LLVM is not complete, some operations such as ```BrOp``` or ```CondOp``` are not yet defined. As a result, we had to extend the LLVM class and write these classes ourselves.       |
| ```xdsl_arm_backend.py```   | This file has our backend, ```ARMBackend```. It takes a module (MLIR's LLVM file) as input and generates the ARM code based on that.        |
| ```xdsl_microc.py```   | This file opens the MLIR file and uses the backend in order to compile it. After the compilation is done the ARM file will be generated in the ```sample_codes``` folder.       |
| ```sample_codes```   | Here you can see all the sample microC files, their LLVM, MLIR and ARM codes. If you want to add a new microC file simply add it here.        |
| ```microc_arm_compile.sh```   | Simply run this executable with the name of the microC file name in the sample_codes folder you want to compile.        |
| ```xdsl_riscv_lowering.py```   | Garbage, in the beginning we wanted to lower the LLVM dialect to RISCV but we changed our approach.        |
| ```pico_implementation```   | How to test the final compiled ARM code in Pico 2.        |