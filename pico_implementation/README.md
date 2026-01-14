# Raspberry Pi Pico 2 Development Setup

This guide describes the required setup for building and flashing firmware to the Raspberry Pi Pico 2.

## 1. Install Required Build Tools and ARM Cross-Compiler

Install the necessary development packages:

```bash
sudo apt install cmake gcc-arm-none-eabi libnewlib-arm-none-eabi libstdc++-arm-none-eabi-newlib
```

## 2. Clone the Raspberry Pi Pico SDK

```bash
git clone https://github.com/raspberrypi/pico-sdk.git
```

## 3. Set the SDK Path in the Environment

```bash
export PICO_SDK_PATH=~/bonus_micro/pico-sdk
```

## 4. Create Project Directory and Import SDK Configuration

```bash
cp pico-sdk/external/pico_sdk_import.cmake <your_project_folder>/
```

The project directory contains:
- C source files  
- ARM assembly code  
- CMake configuration files  
- A build script to automate firmware compilation  

## 5. Build the Firmware

```bash
chmod +x build.sh
./build.sh
```

## 6. Flash the Raspberry Pi Pico 2

1. Connect the Raspberry Pi Pico 2 to your PC while holding the **BOOTSEL** button.  
2. The board will appear as a removable storage device.  
3. Copy the generated firmware file to the device to complete flashing.

(The test_codes.uf2 firmware is ready. Drag and drop it onto the Pico in BOOTSEL mode to flash and run.)
