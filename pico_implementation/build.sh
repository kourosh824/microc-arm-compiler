set -e

rm -rf build
mkdir build
cmake -S . -B build -DPICO_BOARD=pico2_w
cmake --build build -j
