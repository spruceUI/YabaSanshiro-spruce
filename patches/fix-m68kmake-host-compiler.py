#!/usr/bin/env python3
"""Fix m68kmake to build with host compiler during cross-compilation.

m68kmake is a code generator that runs during build. When cross-compiling,
it inherits the cross-compiler and produces an aarch64 binary that can't
run on the x86 build host. Force it to use the native compiler.
"""

with open("yabause/src/CMakeLists.txt", "r") as f:
    content = f.read()

old = """    include(ExternalProject)
    ExternalProject_Add(m68kmake
        DOWNLOAD_COMMAND ""
        SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/musashi
        CMAKE_GENERATOR "${CMAKE_GENERATOR}"
        INSTALL_COMMAND ""
        BINARY_DIR ${CMAKE_CURRENT_BINARY_DIR}/musashi
    )"""

new = """    include(ExternalProject)
    ExternalProject_Add(m68kmake
        DOWNLOAD_COMMAND ""
        SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/musashi
        CMAKE_GENERATOR "${CMAKE_GENERATOR}"
        CMAKE_ARGS -DCMAKE_C_COMPILER=cc -DCMAKE_CXX_COMPILER=c++
        INSTALL_COMMAND ""
        BINARY_DIR ${CMAKE_CURRENT_BINARY_DIR}/musashi
    )"""

content = content.replace(old, new)

with open("yabause/src/CMakeLists.txt", "w") as f:
    f.write(content)

print("Patched m68kmake to use host compiler")
