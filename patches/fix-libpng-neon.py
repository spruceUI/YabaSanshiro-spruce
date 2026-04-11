#!/usr/bin/env python3
"""Fix libpng NEON link errors — use system libpng instead of ExternalProject."""

# Replace the ExternalProject libpng with system libpng via find_package
with open("yabause/CMake/Packages/external_libpng.cmake", "r") as f:
    content = f.read()

# Overwrite the entire file to use system libpng
with open("yabause/CMake/Packages/external_libpng.cmake", "w") as f:
    f.write("""# Use system libpng instead of building from source
find_package(PkgConfig REQUIRED)
pkg_check_modules(PNG REQUIRED libpng)

set(png_INCLUDE_DIR ${PNG_INCLUDE_DIRS})
set(png_STATIC_LIBRARIES ${PNG_LIBRARIES})

# Create a dummy target so add_dependencies(... png ...) doesn't fail
add_custom_target(png)

message(STATUS "Using system libpng: ${PNG_LIBRARIES}")
""")

print("Replaced ExternalProject libpng with system libpng")
