#!/usr/bin/env python3
"""Fix libchd -> libchdr target name mismatch in retro_arena CMakeLists."""

with open("yabause/src/retro_arena/CMakeLists.txt", "r+") as f:
    content = f.read()
    content = content.replace(
        "add_dependencies(yabause-retro-arena Json png zlib libchd nanogui external_sqlite3)",
        "add_dependencies(yabause-retro-arena Json png zlib libchdr nanogui external_sqlite3)",
    )

    f.seek(0)
    f.write(content)


print("Fixed libchd -> libchdr target name")
