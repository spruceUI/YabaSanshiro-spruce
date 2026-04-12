#!/usr/bin/env python3
"""Fix Vulkan C++ API compatibility for Ubuntu 20.04's Vulkan hpp headers."""

with open("yabause/src/ygl_texture.cpp", "r") as f:
    content = f.read()

# createComputePipelines returns ResultValue<vector<Pipeline>> in newer API
# .value is the ResultValue accessor, but Ubuntu 20.04's vulkan.hpp returns
# the vector directly (older API). Replace a.value[0] with a[0]
content = content.replace("a.value[0]", "a[0]")

# CommandBuffer::reset() requires flags argument in newer API
content = content.replace("c.reset();", "c.reset({});")

with open("yabause/src/ygl_texture.cpp", "w") as f:
    f.write(content)

print("Fixed Vulkan C++ API compatibility in ygl_texture.cpp")
