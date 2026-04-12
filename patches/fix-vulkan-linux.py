#!/usr/bin/env python3
"""Fix Vulkan/shaderc for Linux cross-compilation.
Based on mimiki's vulkan-linux-cross-compile.patch."""
import re

with open("yabause/src/CMakeLists.txt", "r") as f:
    content = f.read()

# 1. Replace Android NDK shaderc paths with system/pre-built shaderc (pkgconfig)
content = re.sub(
    r'else\(\)\s*\n\s*set\(\s*LIBVULKAN_INCLUDE[^\n]*vulkan/Include[^\n]*\)\s*\n'
    r'\s*set\(\s*SHADERC_INCLUDE_DIR[^\n]*ANDROID_NDK[^\n]*\)\s*\n'
    r'\s*set\(\s*SHADERC_LIBRARY_DIR[^\n]*ANDROID_NDK[^\n]*\)\s*\n'
    r'\s*set\(\s*SHADERC_LIBRARIES[^\n]*ANDROID_NDK[^\n]*\)\s*\n'
    r'\s*set\(\s*LIBVULKAN\s+vulkan\s*\)',
    """else()
\tset( LIBVULKAN_INCLUDE ${CMAKE_CURRENT_SOURCE_DIR}/vulkan/include)
\tfind_package(PkgConfig)
\tif(PKG_CONFIG_FOUND)
\t\tpkg_check_modules(SHADERC shaderc)
\t\tif(SHADERC_FOUND)
\t\t\tset(SHADERC_INCLUDE_DIR ${SHADERC_INCLUDE_DIRS})
\t\t\tset(SHADERC_LIBRARIES ${SHADERC_LIBRARIES})
\t\telse()
\t\t\tset(SHADERC_INCLUDE_DIR "")
\t\t\tset(SHADERC_LIBRARIES -lshaderc_combined)
\t\tendif()
\telse()
\t\tset(SHADERC_INCLUDE_DIR "")
\t\tset(SHADERC_LIBRARIES -lshaderc_combined)
\tendif()
\tset( LIBVULKAN vulkan )""",
    content
)

# 2. Remove WIN32 guard on shaderc dependency
content = re.sub(
    r'if\s*\(\s*WIN32\s*\)\s*\n\s*add_dependencies\s*\(\s*yabause\s+shaderc\s*\)\s*\n\s*endif\s*\(\s*\)',
    '# shaderc built externally, no cmake target dependency needed',
    content
)

# 3. Disable GLUT requirement when using EGL
content = content.replace(
    'find_package(GLUT)',
    'if(NOT USE_EGL)\n\tfind_package(GLUT)\nendif()'
)

with open("yabause/src/CMakeLists.txt", "w") as f:
    f.write(content)

print("Patched Vulkan/shaderc for Linux cross-compilation")
