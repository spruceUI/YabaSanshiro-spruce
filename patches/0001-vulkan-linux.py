#!/usr/bin/env python3
"""Vulkan Linux cross-compile fixes (from mimiki's 0001 patch).
Applied programmatically to work across different source versions."""

import re

# === 1. CMakeLists.txt: Add Linux Vulkan block, fix GLUT, remove GLFW from Vulkan ===
with open("yabause/src/CMakeLists.txt", "r") as f:
    content = f.read()

# Wrap GLUT in USE_EGL check
content = content.replace(
    "include(FindGLUT)",
    "if(NOT USE_EGL)\n\t\tinclude(FindGLUT)"
)
# Find the endif for GLUT and close our if
content = re.sub(
    r'(set\(YABAUSE_LIBRARIES \$\{YABAUSE_LIBRARIES\} \$\{GLUT_LIBRARIES\}\)\s*\n\s*endif\(\))',
    r'\1\n\t\tendif()',
    content
)

# Add Linux Vulkan block before the Android/else block
# Find the else() that has ANDROID_NDK shaderc paths
content = re.sub(
    r'(\n)(else\(\)\s*\n\s*set\(\s*LIBVULKAN_INCLUDE[^\n]*vulkan/Include)',
    r'''\1elseif(${CMAKE_SYSTEM_NAME} MATCHES "Linux" AND NOT ANDROID)
\tif(USE_VK_KHR_DISPLAY)
\t  add_definitions(-DUSE_VK_KHR_DISPLAY=1)
\tendif()

\tset( LIBVULKAN_INCLUDE ${CMAKE_CURRENT_SOURCE_DIR}/vulkan/include ${CMAKE_CURRENT_SOURCE_DIR}/vulkan/Include)
\tset( LIBVULKAN vulkan )
\tfind_package(PkgConfig)
\tif(PKG_CONFIG_FOUND)
\t\tpkg_check_modules(SHADERC shaderc)
\tendif()
\tif(NOT SHADERC_FOUND)
\t\tinclude(vulkan/external_shaderc.cmake)
\tendif()

\2''',
    content
)

# Remove GLFW from VULKAN_INCLUDE_DIRS and VULKAN_LIBRARIES
content = content.replace(
    "${GLM_INCLUDE_DIRS} ${GLFW_INCLUDE_DIR} ${SHADERC_INCLUDE_DIR}",
    "${GLM_INCLUDE_DIRS} ${SHADERC_INCLUDE_DIR}"
)
content = content.replace(
    "${GLFW_LIBRARIES} ${SHADERC_LIBRARIES}",
    "${SHADERC_LIBRARIES}"
)

with open("yabause/src/CMakeLists.txt", "w") as f:
    f.write(content)
print("Patched CMakeLists.txt for Linux Vulkan")

# === 2. scsp.cpp: Fix time/timespec functions ===
scsp_path = "yabause/src/scsp.cpp"
try:
    with open(scsp_path, "r") as f:
        scsp = f.read()
    scsp = scsp.replace("        time(&tm);", "        clock_gettime(CLOCK_REALTIME, &tm);")
    scsp = scsp.replace("pthread_cond_timedwait(&sync_cnd,&sync_mutex,ctime(&tm))",
                         "pthread_cond_timedwait(&sync_cnd,&sync_mutex,&tm)")
    with open(scsp_path, "w") as f:
        f.write(scsp)
    print("Patched scsp.cpp")
except FileNotFoundError:
    print("scsp.cpp not found, skipping")

# === 3. Platform.cpp: Add VK_KHR_DISPLAY platform init ===
with open("yabause/src/vulkan/Platform.cpp", "r") as f:
    plat = f.read()

if "USE_VK_KHR_DISPLAY" not in plat:
    # Add before the final #endif
    plat = plat.rstrip()
    if plat.endswith("#endif"):
        plat = plat[:-6] + """
#elif defined(USE_VK_KHR_DISPLAY)

void InitPlatform()
{
}

void DeInitPlatform()
{
}

void AddRequiredPlatformInstanceExtensions(std::vector<const char *> *instance_extensions)
{
  instance_extensions->push_back(VK_KHR_DISPLAY_EXTENSION_NAME);
}

#endif
"""
    with open("yabause/src/vulkan/Platform.cpp", "w") as f:
        f.write(plat)
    print("Patched Platform.cpp")

# === 4. Platform.h: Add VK_KHR_DISPLAY section, remove SDL Vulkan includes ===
with open("yabause/src/vulkan/Platform.h", "r") as f:
    plath = f.read()

# Add VK_KHR_DISPLAY block before Linux XCB block
plath = plath.replace(
    "// LINUX ( Via XCB library )",
    """// VK_KHR_display: no windowing system headers needed
#elif defined(USE_VK_KHR_DISPLAY)

// Purposely empty

// LINUX ( Via XCB library )"""
)

# Remove SDL Vulkan includes (they pull in X11)
plath = re.sub(
    r'#if defined\(HAVE_LIBSDL2\)\s*\n\s*#include <SDL\.h>\s*\n\s*#include <SDL_vulkan\.h>\s*\n\s*#endif\s*\n',
    '',
    plath
)
plath = plath.replace('#include <SDL2/SDL_vulkan.h>', '')
plath = plath.replace('// #include <SDL2/SDL_vulkan.h> // disabled for embedded Linux', '')

with open("yabause/src/vulkan/Platform.h", "w") as f:
    f.write(plath)
print("Patched Platform.h")

# === 5. BUILD_OPTIONS.h: Disable GLFW on Linux ===
with open("yabause/src/vulkan/BUILD_OPTIONS.h", "r") as f:
    bo = f.read()

bo = bo.replace(
    "#if defined(ANDROID)",
    "#if defined(ANDROID) || defined(__linux__)"
)

with open("yabause/src/vulkan/BUILD_OPTIONS.h", "w") as f:
    f.write(bo)
print("Patched BUILD_OPTIONS.h")
