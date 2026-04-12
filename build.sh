#!/bin/bash
set -e

YABA_VERSION="${YABA_VERSION:-a40dace1ae0af3ebd45848549fdf396f40e3930f}"
OUTPUT_DIR="${OUTPUT_DIR:-/output}"
CROSS=aarch64-linux-gnu

export CC=${CROSS}-gcc
export CXX=${CROSS}-g++
export AR=${CROSS}-ar
export STRIP=${CROSS}-strip
export PKG_CONFIG_PATH=/usr/lib/${CROSS}/pkgconfig
export PKG_CONFIG_LIBDIR=/usr/lib/${CROSS}/pkgconfig

# ccache setup
export CCACHE_DIR="${CCACHE_DIR:-/ccache}"
export PATH="/usr/lib/ccache:$PATH"
ln -sf /usr/bin/ccache /usr/local/bin/${CROSS}-gcc
ln -sf /usr/bin/ccache /usr/local/bin/${CROSS}-g++
ccache --max-size=1G
ccache --zero-stats

# Allow old cmake_minimum_required in ExternalProjects
export CMAKE_POLICY_VERSION_MINIMUM=3.5

# ============================================================
# Clone YabaSanshiro
# ============================================================
echo "=== Cloning YabaSanshiro ==="
git clone --recursive https://github.com/sydarn/yabause.git yabasanshiro
cd yabasanshiro
git checkout "$YABA_VERSION"
git submodule update --init --recursive

# ============================================================
# Pre-compile host tools (must run on build machine, not target)
# ============================================================
echo "=== Building host tools ==="
cc yabause/src/retro_arena/nanogui-sdl/resources/bin2c.c -o bin2c_host
cc yabause/src/musashi/m68kmake.c -o m68kmake_host

# Patch CMakeLists to use host-compiled tools
sed -i "s|COMMAND \./bin2c|COMMAND $PWD/bin2c_host|g" yabause/src/retro_arena/nanogui-sdl/CMakeLists.txt
sed -i "s|COMMAND \$<TARGET_FILE:bin2c>|COMMAND $PWD/bin2c_host|g" yabause/src/retro_arena/nanogui-sdl/CMakeLists.txt
sed -i "s|add_executable(bin2c resources/bin2c.c)|add_custom_target(bin2c DEPENDS $PWD/bin2c_host)|g" yabause/src/retro_arena/nanogui-sdl/CMakeLists.txt

sed -i "s|COMMAND m68kmake|COMMAND $PWD/m68kmake_host|g" yabause/src/musashi/CMakeLists.txt
sed -i "s|add_executable(m68kmake m68kmake.c)|# m68kmake built as host tool|g" yabause/src/musashi/CMakeLists.txt
sed -i "s|DEPENDS m68kmake.c|DEPENDS|g" yabause/src/musashi/CMakeLists.txt

# ============================================================
# Build shaderc from source (needed for Vulkan shader compilation)
# ============================================================
echo "=== Building shaderc ==="
SHADERC_PREFIX=/build/shaderc-install
git clone https://github.com/google/shaderc.git /build/shaderc-src
cd /build/shaderc-src
git checkout v2020.5
python3 utils/git-sync-deps
mkdir -p build && cd build
cmake .. \
    -DCMAKE_C_COMPILER=${CROSS}-gcc \
    -DCMAKE_CXX_COMPILER=${CROSS}-g++ \
    -DCMAKE_SYSTEM_NAME=Linux \
    -DCMAKE_SYSTEM_PROCESSOR=aarch64 \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$SHADERC_PREFIX" \
    -DSHADERC_SKIP_TESTS=ON \
    -DSHADERC_SKIP_EXAMPLES=ON \
    -DSHADERC_SKIP_INSTALL=OFF
make -j$(nproc)
make install
cd /build/yabasanshiro

# Add shaderc to pkg-config path
export PKG_CONFIG_PATH="${SHADERC_PREFIX}/lib/pkgconfig:$PKG_CONFIG_PATH"

# ============================================================
# Copy kmsdrm port into source tree (mimiki's Vulkan display port)
# ============================================================
echo "=== Installing kmsdrm port ==="
mkdir -p yabause/src/kmsdrm
cp /kmsdrm/* yabause/src/kmsdrm/

# Apply patches (mimiki's Vulkan + libchdr cross-compile patches)
for patch in /patches/*.patch; do
    [ -f "$patch" ] && git apply "$patch" && echo "Applied: $(basename $patch)"
done
for patch in /patches/*.py; do
    [ -f "$patch" ] && python3 "$patch" && echo "Applied: $(basename $patch)"
done

# Prevent EGL from including X11 headers
sed -i 's|#include <X11/Xlib.h>|// X11 disabled for embedded\n// #include <X11/Xlib.h>|g' /usr/include/aarch64-linux-gnu/EGL/eglplatform.h 2>/dev/null || true
sed -i 's|#include <X11/Xutil.h>|// #include <X11/Xutil.h>|g' /usr/include/aarch64-linux-gnu/EGL/eglplatform.h 2>/dev/null || true
echo "Disabled X11 in EGL headers"

# Nuke ALL X11/Xlib/XCB Vulkan platform includes everywhere
for vkh in $(find /usr/include yabause/src/vulkan -name "vulkan.h" -o -name "vulkan_core.h" 2>/dev/null); do
    sed -i 's/#ifdef VK_USE_PLATFORM_XLIB_KHR/#if 0/g' "$vkh"
    sed -i 's/#ifdef VK_USE_PLATFORM_XCB_KHR/#if 0/g' "$vkh"
    sed -i 's/#ifdef VK_USE_PLATFORM_XLIB_XRANDR_EXT/#if 0/g' "$vkh"
done
# Also disable XCB block in Platform.h (it includes X11 headers)
sed -i 's|#elif defined( __linux )|#elif 0 // XCB disabled for kmsdrm|g' yabause/src/vulkan/Platform.h
echo "Disabled all X11/XCB Vulkan platform headers"

# ============================================================
# Build YabaSanshiro
# ============================================================
echo "=== Building YabaSanshiro ==="
mkdir -p build && cd build
cmake ../yabause \
    -DCMAKE_TOOLCHAIN_FILE=../yabause/src/retro_arena/n2.cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_FLAGS="-O3 -I${SHADERC_PREFIX}/include -DUSE_VK_KHR_DISPLAY=1 -DMESA_EGL_NO_X11_HEADERS" \
    -DCMAKE_CXX_FLAGS="-O3 -I${SHADERC_PREFIX}/include -DUSE_VK_KHR_DISPLAY=1 -DMESA_EGL_NO_X11_HEADERS" \
    -DCMAKE_EXE_LINKER_FLAGS="-L${SHADERC_PREFIX}/lib" \
    -DSHADERC_FOUND=1 \
    -DSHADERC_INCLUDE_DIRS="${SHADERC_PREFIX}/include" \
    -DSHADERC_LIBRARIES="-lshaderc_combined" \
    -DYAB_PORTS=kmsdrm \
    -DYAB_WANT_ARM7=ON \
    -DYAB_WANT_DYNAREC_DEVMIYAX=ON \
    -DYAB_WANT_VULKAN=ON \
    -DYAB_WANT_SDL=ON \
    -DYAB_WANT_OPENAL=OFF \
    -DYAB_WANT_OPENGL=ON \
    -DUSE_EGL=ON \
    -DUSE_VK_KHR_DISPLAY=ON \
    -DYAB_MULTIBUILD=OFF \
    -DCMAKE_DISABLE_FIND_PACKAGE_GLUT=TRUE
make -j$(nproc)
cd /build

# ============================================================
# Collect output
# ============================================================
echo "=== Collecting output ==="
mkdir -p "$OUTPUT_DIR/libs"

# Find the yabasanshiro binary (kmsdrm port outputs yabause-kmsdrm)
YABA_BIN=$(find yabasanshiro/build -name "yabause-kmsdrm" -type f -executable | head -1)
if [ -z "$YABA_BIN" ]; then
    YABA_BIN=$(find yabasanshiro/build -name "yabasanshiro" -type f -executable | head -1)
fi
if [ -n "$YABA_BIN" ]; then
    cp "$YABA_BIN" "$OUTPUT_DIR/yabasanshiro"
    ${STRIP} -s "$OUTPUT_DIR/yabasanshiro"
    echo "Binary: $YABA_BIN"
else
    echo "ERROR: Could not find built binary"
    find yabasanshiro/build -type f -executable
    exit 1
fi

# Collect shared library dependencies
SKIP_LIBS="linux-vdso|ld-linux|libc\.so|libm\.so|libdl\.so|libpthread\.so|librt\.so|libgcc_s|libstdc\+\+|libSDL2|libasound|libudev|libdrm|libwayland|libEGL|libGLES|libMali|libgomp|libvulkan|libmali|libIMGegl|libsrv_um|libusc|libGL\.so|libGLX|libGLdispatch|libglut"

collect_deps() {
    local binary="$1"
    ${CROSS}-readelf -d "$binary" 2>/dev/null | grep NEEDED | sed 's/.*\[\(.*\)\]/\1/' | while read -r lib; do
        [ -f "$OUTPUT_DIR/libs/$lib" ] && continue
        echo "$lib" | grep -qE "$SKIP_LIBS" && continue

        local src
        src=$(find "/usr/lib/${CROSS}" "/lib/${CROSS}" -maxdepth 1 -name "$lib" 2>/dev/null | head -1)
        if [ -n "$src" ]; then
            cp -L "$src" "$OUTPUT_DIR/libs/$lib"
            echo "  Collected: $lib"
            collect_deps "$OUTPUT_DIR/libs/$lib"
        else
            echo "  WARNING: $lib not found"
        fi
    done
}

echo "Collecting transitive dependencies..."
collect_deps "$OUTPUT_DIR/yabasanshiro"
for lib in "$OUTPUT_DIR"/libs/*.so*; do
    collect_deps "$lib"
done

# Strip all collected libs
for so in "$OUTPUT_DIR"/libs/*.so*; do
    ${STRIP} -s "$so" 2>/dev/null || true
done

echo "=== ccache stats ==="
ccache --show-stats

echo "=== Build complete ==="
ls -la "$OUTPUT_DIR/"
ls -la "$OUTPUT_DIR/libs/"
