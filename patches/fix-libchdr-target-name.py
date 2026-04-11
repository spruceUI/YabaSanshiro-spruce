#!/usr/bin/env python3
"""Fix libchd -> libchdr target name mismatch in retro_arena CMakeLists."""

with open("yabause/src/retro_arena/CMakeLists.txt", "r") as f:
    content = f.read()

# Simple replace that works regardless of surrounding deps
content = content.replace("libchd ", "libchdr ")
content = content.replace("libchd)", "libchdr)")

with open("yabause/src/retro_arena/CMakeLists.txt", "w") as f:
    f.write(content)

print("Fixed libchd -> libchdr target name")
