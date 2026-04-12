#!/usr/bin/env python3
"""Add SDL2 Vulkan window backend for Linux embedded targets."""
import os

# 1. Create Window_sdl.cpp
window_sdl = '''#include "BUILD_OPTIONS.h"
#include "Platform.h"

#include "Window.h"
#include "Shared.h"
#include "Renderer.h"

#include <assert.h>

#if BUILD_USE_SDL_VULKAN

#include <SDL2/SDL.h>
#include <SDL2/SDL_vulkan.h>

static SDL_Window *_sdl_window = nullptr;

void Window::_InitOSWindow()
{
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        assert(0 && "SDL_Init failed");
    }
    _sdl_window = SDL_CreateWindow(
        _window_name.c_str(),
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        _surface_size_x, _surface_size_y,
        SDL_WINDOW_VULKAN | SDL_WINDOW_FULLSCREEN
    );
    assert(_sdl_window && "SDL_CreateWindow failed");

    int w, h;
    SDL_Vulkan_GetDrawableSize(_sdl_window, &w, &h);
    _surface_size_x = w;
    _surface_size_y = h;
}

void Window::_DeInitOSWindow()
{
    if (_sdl_window) {
        SDL_DestroyWindow(_sdl_window);
        _sdl_window = nullptr;
    }
}

void Window::_UpdateOSWindow()
{
    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        if (event.type == SDL_QUIT) {
            Close();
        }
    }
}

void Window::_InitOSSurface()
{
    if (!SDL_Vulkan_CreateSurface(_sdl_window, _renderer->GetVulkanInstance(), &_surface)) {
        assert(0 && "SDL_Vulkan_CreateSurface failed");
    }
}

#endif // BUILD_USE_SDL_VULKAN
'''

with open("yabause/src/vulkan/Window_sdl.cpp", "w") as f:
    f.write(window_sdl)
print("Created Window_sdl.cpp")

# 2. Patch BUILD_OPTIONS.h
with open("yabause/src/vulkan/BUILD_OPTIONS.h", "r") as f:
    content = f.read()

content = content.replace(
    """#if defined(ANDROID) || defined(__linux__)
// GLFW disabled for Android and Linux embedded targets
#else
#define BUILD_USE_GLFW											1
#endif""",
    """#if defined(ANDROID)
// Android uses native windowing
#elif defined(__linux__)
#define BUILD_USE_SDL_VULKAN									1
#else
#define BUILD_USE_GLFW											1
#endif"""
)

with open("yabause/src/vulkan/BUILD_OPTIONS.h", "w") as f:
    f.write(content)
print("Patched BUILD_OPTIONS.h")

# 3. Patch Platform.h — add SDL Vulkan includes for our backend
with open("yabause/src/vulkan/Platform.h", "r") as f:
    content = f.read()

content = content.replace(
    "// #include <SDL2/SDL_vulkan.h> // disabled for embedded Linux",
    """#if BUILD_USE_SDL_VULKAN
#include <SDL2/SDL.h>
#include <SDL2/SDL_vulkan.h>
#endif"""
)

# Also undef Window in Window.h and Renderer.h before class definition
for hdr in ["yabause/src/vulkan/Window.h", "yabause/src/vulkan/Renderer.h"]:
    with open(hdr, "r") as f:
        h = f.read()
    # Add undef before the class declaration
    h = h.replace("class Window {", "#ifdef Window\\n#undef Window\\n#endif\\nclass Window {")
    h = h.replace("class Window;", "#ifdef Window\\n#undef Window\\n#endif\\nclass Window;")
    # Fix escaped newlines
    h = h.replace("\\n", "\n")
    with open(hdr, "w") as f:
        f.write(h)
print("Added #undef Window to Window.h and Renderer.h")

with open("yabause/src/vulkan/Platform.h", "w") as f:
    f.write(content)
print("Patched Platform.h")

# 4. Add Window_sdl.cpp to VULKAN_SOURCES in CMakeLists.txt
with open("yabause/src/CMakeLists.txt", "r") as f:
    content = f.read()

content = content.replace(
    "vulkan/Window.cpp",
    "vulkan/Window.cpp\n vulkan/Window_sdl.cpp\n vulkan/Window_glfw.cpp"
)

with open("yabause/src/CMakeLists.txt", "w") as f:
    f.write(content)
print("Added Window_sdl.cpp and Window_glfw.cpp to cmake sources")
