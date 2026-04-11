#!/usr/bin/env python3
"""Fix nanogui bin2c to build with host compiler during cross-compilation.

bin2c is a resource compiler that runs during build. When cross-compiling,
it gets built for aarch64 and can't execute on x86. Build it separately
with the native compiler.
"""
import subprocess
import os

# Build bin2c with the host compiler before cmake runs
src = "yabause/src/retro_arena/nanogui-sdl/resources/bin2c.c"
out = "yabause/src/retro_arena/nanogui-sdl/bin2c_host"

subprocess.run(["cc", "-o", out, src], check=True)
os.chmod(out, 0o755)

# Patch CMakeLists to use pre-built host binary instead of cross-compiled one
cmake_path = "yabause/src/retro_arena/nanogui-sdl/CMakeLists.txt"
with open(cmake_path, "r") as f:
    content = f.read()

# Replace the add_executable and use our pre-built host binary
content = content.replace(
    "add_executable(bin2c resources/bin2c.c)",
    "# bin2c pre-built for host (cross-compile fix)\n"
    "add_custom_target(bin2c DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/bin2c_host)"
)
content = content.replace(
    "COMMAND $<TARGET_FILE:bin2c>",
    "COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/bin2c_host"
)

with open(cmake_path, "w") as f:
    f.write(content)

print("Patched nanogui bin2c to use host-compiled binary")
