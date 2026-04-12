#!/usr/bin/env python3
"""Fix Vulkan C++ API compatibility for Ubuntu 20.04's Vulkan hpp headers."""

with open("yabause/src/ygl_texture.cpp", "r") as f:
    content = f.read()

# CommandBuffer::reset() requires flags argument in newer Vulkan hpp
content = content.replace("c.reset();", "c.reset({});")

with open("yabause/src/ygl_texture.cpp", "w") as f:
    f.write(content)

print("Fixed Vulkan C++ API compatibility in ygl_texture.cpp")
