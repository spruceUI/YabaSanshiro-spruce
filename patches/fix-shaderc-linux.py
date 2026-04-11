#!/usr/bin/env python3
"""Fix shaderc for Linux: add external_shaderc.cmake include in else() block."""

with open("yabause/src/CMakeLists.txt", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    # After the else() inside the Vulkan block, inject the shaderc include
    # and replace the Android NDK shaderc paths
    if 'LIBVULKAN_INCLUDE' in line and 'vulkan/Include' in line:
        # This is the line: set( LIBVULKAN_INCLUDE ${CMAKE_CURRENT_SOURCE_DIR}/vulkan/Include)
        # Add shaderc include before it
        new_lines.insert(-1, '\tinclude(vulkan/external_shaderc.cmake)\n')
        # Fix the case: Include -> include
        new_lines[-1] = new_lines[-1].replace('vulkan/Include', 'vulkan/include')

# Remove the Android NDK SHADERC lines
final_lines = []
for line in new_lines:
    if 'ANDROID_NDK' in line and 'shaderc' in line.lower():
        continue
    final_lines.append(line)

with open("yabause/src/CMakeLists.txt", "w") as f:
    f.writelines(final_lines)

print("Patched shaderc to build from source on Linux")
