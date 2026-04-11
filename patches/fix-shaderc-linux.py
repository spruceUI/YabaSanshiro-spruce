#!/usr/bin/env python3
"""Fix shaderc paths for Linux cross-compilation instead of Android NDK."""

with open("yabause/src/CMakeLists.txt", "r") as f:
    content = f.read()

old = """else()
	set( LIBVULKAN_INCLUDE ${CMAKE_CURRENT_SOURCE_DIR}/vulkan/Include)
	set( SHADERC_INCLUDE_DIR ${ANDROID_NDK}/sources/third_party/shaderc/include  )
	set( SHADERC_LIBRARY_DIR ${ANDROID_NDK}/sources/third_party/shaderc/libs/c++_shared/${ANDROID_ABI}  )
	set( SHADERC_LIBRARIES ${ANDROID_NDK}/sources/third_party/shaderc/libs/c++_shared/${ANDROID_ABI}/libshaderc.a  )
	set( LIBVULKAN vulkan )
endif()"""

new = """else()
	set( LIBVULKAN_INCLUDE ${CMAKE_CURRENT_SOURCE_DIR}/vulkan/Include)
	find_path(SHADERC_INCLUDE_DIR shaderc/shaderc.hpp)
	find_library(SHADERC_LIBRARIES shaderc_combined NAMES shaderc_shared shaderc)
	set( LIBVULKAN vulkan )
endif()"""

content = content.replace(old, new)

with open("yabause/src/CMakeLists.txt", "w") as f:
    f.write(content)

print("Patched shaderc to use system paths on Linux")
