#!/usr/bin/env python3
"""Fix libpng NEON link errors — disable ARM NEON in ExternalProject libpng 1.6."""

with open("yabause/CMake/Packages/external_libpng.cmake", "r") as f:
    content = f.read()

# Add PNG_ARM_NEON=off to disable NEON asm that fails to link during cross-compilation
content = content.replace(
    "-DPNG_SHARED:BOOL=OFF",
    "-DPNG_SHARED:BOOL=OFF\n        -DPNG_ARM_NEON=off"
)

with open("yabause/CMake/Packages/external_libpng.cmake", "w") as f:
    f.write(content)

print("Disabled libpng ARM NEON optimizations")
