#!/usr/bin/env python3
"""Fix libchdr cross-compilation (from mimiki's 0002 patch)."""
import re, os

path = "yabause/CMake/Packages/external_libchdr.cmake"
with open(path, "r") as f:
    content = f.read()

# Add cross-compilation toolchain passthrough before the else() block
if "CMAKE_CROSSCOMPILING" not in content:
    content = content.replace(
        "else()\n  set(ADDITIONAL_CMAKE_ARGS \"\")\nendif()",
        """elseif(CMAKE_CROSSCOMPILING AND CMAKE_TOOLCHAIN_FILE)
  get_filename_component(TOOL_CHAIN_ABSOLUTE_PATH "${CMAKE_TOOLCHAIN_FILE}"
                         REALPATH BASE_DIR "${CMAKE_BINARY_DIR}")
  set(ADDITIONAL_CMAKE_ARGS
    -DCMAKE_TOOLCHAIN_FILE=${TOOL_CHAIN_ABSOLUTE_PATH}
    -DWITH_LZMA_ASM=OFF
  )
else()
  set(ADDITIONAL_CMAKE_ARGS "")
endif()"""
    )

    # Add cross-compile library paths
    content = content.replace(
        " set( LIBCHDR_LIB_DIR ${BINARY_DIR} )\nelse()",
        """ set( LIBCHDR_LIB_DIR ${BINARY_DIR} )
elseif(CMAKE_CROSSCOMPILING)
set(LIBCHDR_LIBRARIES
 ${BINARY_DIR}/${CMAKE_STATIC_LIBRARY_PREFIX}chdr-static${CMAKE_STATIC_LIBRARY_SUFFIX}
 ${BINARY_DIR}/deps/lzma-24.05/${CMAKE_STATIC_LIBRARY_PREFIX}lzma${CMAKE_STATIC_LIBRARY_SUFFIX}
 ${BINARY_DIR}/deps/zstd-1.5.6/build/cmake/lib/${CMAKE_STATIC_LIBRARY_PREFIX}zstd${CMAKE_STATIC_LIBRARY_SUFFIX}
 )
 set( LIBCHDR_LIB_DIR ${BINARY_DIR} )
else()"""
    )

with open(path, "w") as f:
    f.write(content)

print("Patched libchdr for cross-compilation")
