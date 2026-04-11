#!/usr/bin/env python3
"""Fix shaderc dependency — must apply to all platforms, not just Windows."""
import re

with open("yabause/src/CMakeLists.txt", "r") as f:
    content = f.read()

# Remove the WIN32 guard around add_dependencies(yabause shaderc)
# so it applies on all platforms
content = content.replace("if(WIN32)\n\t\tadd_dependencies(yabause shaderc)\n\tendif()", "add_dependencies(yabause shaderc)")

with open("yabause/src/CMakeLists.txt", "w") as f:
    f.write(content)

print("Fixed shaderc dependency for all platforms")
