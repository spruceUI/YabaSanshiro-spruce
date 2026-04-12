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

# 4. Disable GLFW in BUILD_OPTIONS.h for Linux (not just Android)
with open("yabause/src/vulkan/BUILD_OPTIONS.h", "r") as f:
    bo = f.read()

bo = bo.replace(
    """#if defined(ANDROID)
#else
#define BUILD_USE_GLFW											1
#endif""",
    """#if defined(ANDROID) || defined(__linux__)
// GLFW disabled for Android and Linux embedded targets
#else
#define BUILD_USE_GLFW											1
#endif"""
)

with open("yabause/src/vulkan/BUILD_OPTIONS.h", "w") as f:
    f.write(bo)

# 5. Remove SDL2 Vulkan include from Platform.h (mimiki does this)
with open("yabause/src/vulkan/Platform.h", "r") as f:
    ph = f.read()

ph = ph.replace('#include <SDL2/SDL_vulkan.h>', '// #include <SDL2/SDL_vulkan.h> // disabled for embedded Linux')

with open("yabause/src/vulkan/Platform.h", "w") as f:
    f.write(ph)

# 6. Prevent Vulkan from including X11 headers that define Window typedef
# The bundled vulkan headers auto-detect X11 and include xlib surface headers
# which typedef Window = unsigned long, conflicting with our Window class.
# We don't need Xlib Vulkan — we use SDL for surface creation.
vulkan_core = "yabause/src/vulkan/include/vulkan/vulkan.h"
import os
if os.path.exists(vulkan_core):
    with open(vulkan_core, "r") as f:
        vc = f.read()
    vc = vc.replace('#ifdef VK_USE_PLATFORM_XLIB_KHR', '#if 0 // VK_USE_PLATFORM_XLIB_KHR disabled for SDL Vulkan')
    vc = vc.replace('#ifdef VK_USE_PLATFORM_XLIB_XRANDR_EXT', '#if 0 // VK_USE_PLATFORM_XLIB_XRANDR_EXT disabled')
    with open(vulkan_core, "w") as f:
        f.write(vc)
    print("Disabled Xlib Vulkan platform headers")
else:
    # Try system vulkan headers path
    print("WARNING: bundled vulkan.h not found, X11 Window conflict may persist")

print("Patched Vulkan/shaderc/GLFW for Linux cross-compilation")
