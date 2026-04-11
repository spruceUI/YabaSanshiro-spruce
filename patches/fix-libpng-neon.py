#!/usr/bin/env python3
"""Fix libpng NEON link errors — disable hardware optimizations in ExternalProject libpng."""

with open("yabause/CMake/Packages/external_libpng.cmake", "r") as f:
    content = f.read()

# Add PNG_HARDWARE_OPTIMIZATIONS=OFF to disable NEON asm that fails to link
content = content.replace(
    "-DCMAKE_BUILD_TYPE=Release",
    "-DCMAKE_BUILD_TYPE=Release -DPNG_HARDWARE_OPTIMIZATIONS=OFF"
)

with open("yabause/CMake/Packages/external_libpng.cmake", "w") as f:
    f.write(content)

print("Disabled libpng NEON hardware optimizations")
