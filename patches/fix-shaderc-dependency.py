#!/usr/bin/env python3
"""Fix shaderc dependency — must apply to all platforms, not just Windows."""

with open("yabause/src/CMakeLists.txt", "r") as f:
    content = f.read()

content = content.replace(
    """if(YAB_WANT_VULKAN)
	if(WIN32)
		add_dependencies(yabause shaderc)
	endif()
add_dependencies(yabause glm)
endif(YAB_WANT_VULKAN)""",
    """if(YAB_WANT_VULKAN)
	add_dependencies(yabause shaderc)
	add_dependencies(yabause glm)
endif(YAB_WANT_VULKAN)"""
)

with open("yabause/src/CMakeLists.txt", "w") as f:
    f.write(content)

print("Fixed shaderc dependency for all platforms")
