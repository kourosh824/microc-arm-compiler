# Raspberry Pi Pico 2 Development Setup
### Install required build tools and ARM cross-compiler:

sudo apt install cmake gcc-arm-none-eabi libnewlib-arm-none-eabi libstdc++-arm-none-eabi-newlib

### Clone the Raspberry Pi Pico SDK locally:

git clone https://github.com/raspberrypi/pico-sdk.git

### Set the SDK path in the environment:

export PICO_SDK_PATH=~/bonus_micro/pico-sdk

### Create a project directory and copy the SDK import file:

cp pico-sdk/external/pico_sdk_import.cmake <your_project_folder>/ 

### The project directory contained the C sources, ARM assembly code, CMake configuration, and a build script to automate the firmware compilation process.

## Build and Flash Procedure

### Generate the firmware file by running the build script (after granting execution permission):

chmod +x build.sh
./build.sh

### Connect the Raspberry Pi Pico 2 to the PC while holding the BOOTSEL button. The board will appear as a removable storage device.

### Drag and drop the generated .uf2 file into the Pico storage folder. The device will automatically disconnect and execute the uploaded firmware.