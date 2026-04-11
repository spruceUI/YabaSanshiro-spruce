#!/usr/bin/env python3
"""Fix sqlite3 ExternalProject cmake_minimum_required version for cmake 4.x."""

with open("yabause/src/retro_arena/CMakeLists.txt", "r") as f:
    content = f.read()

content = content.replace(
    'COMMAND echo cmake_minimum_required( VERSION 3.2 ) > ${sqlite3_cmake_file_path}',
    'COMMAND echo cmake_minimum_required( VERSION 3.10 ) > ${sqlite3_cmake_file_path}'
)

with open("yabause/src/retro_arena/CMakeLists.txt", "w") as f:
    f.write(content)

print("Fixed sqlite3 cmake_minimum_required version")
