#!/usr/bin/env python3
"""Fix shaderc for Linux: use the external_shaderc.cmake for all platforms, not just Windows."""

with open("yabause/src/CMakeLists.txt", "r") as f:
    content = f.read()

# Make external_shaderc.cmake build for all platforms, not just Windows
old = """if (${CMAKE_SYSTEM_NAME} MATCHES "Windows")
  include(vulkan/external_shaderc.cmake)
	include(vulkan/external_glfw.cmake)
	set(LIBVULKAN_INCLUDE ${CMAKE_CURRENT_SOURCE_DIR}/vulkan/include)

	if(CMAKE_SIZEOF_VOID_P EQUAL 8)
		set(LIBVULKAN ${CMAKE_CURRENT_SOURCE_DIR}/vulkan/lib/x86_64/vulkan-1.lib )
	else()
		set(LIBVULKAN ${CMAKE_CURRENT_SOURCE_DIR}/vulkan/lib/x86/vulkan-1.lib )
	endif()

else()
	set( LIBVULKAN_INCLUDE ${CMAKE_CURRENT_SOURCE_DIR}/vulkan/Include)
	set( SHADERC_INCLUDE_DIR ${ANDROID_NDK}/sources/third_party/shaderc/include  )
	set( SHADERC_LIBRARY_DIR ${ANDROID_NDK}/sources/third_party/shaderc/libs/c++_shared/${ANDROID_ABI}  )
	set( SHADERC_LIBRARIES ${ANDROID_NDK}/sources/third_party/shaderc/libs/c++_shared/${ANDROID_ABI}/libshaderc.a  )
	set( LIBVULKAN vulkan )
endif()"""

new = """if (${CMAKE_SYSTEM_NAME} MATCHES "Windows")
  include(vulkan/external_shaderc.cmake)
	include(vulkan/external_glfw.cmake)
	set(LIBVULKAN_INCLUDE ${CMAKE_CURRENT_SOURCE_DIR}/vulkan/include)

	if(CMAKE_SIZEOF_VOID_P EQUAL 8)
		set(LIBVULKAN ${CMAKE_CURRENT_SOURCE_DIR}/vulkan/lib/x86_64/vulkan-1.lib )
	else()
		set(LIBVULKAN ${CMAKE_CURRENT_SOURCE_DIR}/vulkan/lib/x86/vulkan-1.lib )
	endif()

else()
	include(vulkan/external_shaderc.cmake)
	set( LIBVULKAN_INCLUDE ${CMAKE_CURRENT_SOURCE_DIR}/vulkan/include)
	set( LIBVULKAN vulkan )
endif()"""

content = content.replace(old, new)

with open("yabause/src/CMakeLists.txt", "w") as f:
    f.write(content)

print("Patched shaderc to build from source on Linux")
