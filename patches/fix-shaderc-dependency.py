#!/usr/bin/env python3
"""Fix shaderc dependency — must apply to all platforms, not just Windows."""
import re

with open("yabause/src/CMakeLists.txt", "r") as f:
    content = f.read()

# Match the WIN32 guard around shaderc regardless of whitespace
content = re.sub(
    r'if\s*\(\s*WIN32\s*\)\s*\n\s*add_dependencies\s*\(\s*yabause\s+shaderc\s*\)\s*\n\s*endif\s*\(\s*\)',
    'add_dependencies(yabause shaderc)',
    content
)

with open("yabause/src/CMakeLists.txt", "w") as f:
    f.write(content)

print("Fixed shaderc dependency for all platforms")
