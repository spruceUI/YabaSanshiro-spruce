#!/bin/bash
set -e

YABA_VERSION="${YABA_VERSION:-master}"
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

# ============================================================
# Clone and build YabaSanshiro
# ============================================================
# Allow old cmake_minimum_required in ExternalProjects (libpng, sqlite3, etc.)
export CMAKE_POLICY_VERSION_MINIMUM=3.5

echo "=== Building YabaSanshiro ==="
git clone --recursive https://github.com/devmiyax/yabause.git yabasanshiro
cd yabasanshiro
if [ "$YABA_VERSION" != "master" ]; then
    git checkout "$YABA_VERSION"
fi

# Apply patches
for patch in /patches/*.patch; do
    [ -f "$patch" ] && git apply "$patch" && echo "Applied: $(basename $patch)"
done
for patch in /patches/*.py; do
    [ -f "$patch" ] && python3 "$patch" && echo "Applied: $(basename $patch)"
done

mkdir -p build && cd build
cmake ../yabause \
    -DCMAKE_SYSTEM_NAME=Linux \
    -DCMAKE_SYSTEM_PROCESSOR=aarch64 \
    -DCMAKE_C_COMPILER=${CROSS}-gcc \
    -DCMAKE_CXX_COMPILER=${CROSS}-g++ \
    -DCMAKE_FIND_ROOT_PATH="/usr/${CROSS};/usr" \
    -DCMAKE_FIND_ROOT_PATH_MODE_LIBRARY=ONLY \
    -DCMAKE_FIND_ROOT_PATH_MODE_INCLUDE=BOTH \
    -DCMAKE_FIND_ROOT_PATH_MODE_PROGRAM=NEVER \
    -DCMAKE_LIBRARY_PATH="/usr/lib/${CROSS}" \
    -DCMAKE_INCLUDE_PATH="/usr/include" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_FLAGS="-O3" \
    -DCMAKE_CXX_FLAGS="-O3" \
    -DCMAKE_EXE_LINKER_FLAGS="-L/usr/lib/${CROSS} -Wl,-rpath-link,/usr/lib/${CROSS}" \
    -DYAB_PORTS=retro_arena \
    -DYAB_WANT_OPENGL=ON \
    -DYAB_WANT_SDL=ON \
    -DYAB_WANT_VULKAN=OFF \
    -DYAB_WANT_DYNAREC_DEVMIYAX=ON \
    -DYAB_MULTIBUILD=OFF
make -j$(nproc)
cd /build

# ============================================================
# Collect output
# ============================================================
echo "=== Collecting output ==="
mkdir -p "$OUTPUT_DIR/libs"

# Find and copy the yabasanshiro binary
YABA_BIN=$(find yabasanshiro/build -name "yabasanshiro" -type f -executable | head -1)
if [ -z "$YABA_BIN" ]; then
    YABA_BIN=$(find yabasanshiro/build -name "yabause" -type f -executable | head -1)
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
# Skip device-provided libs
SKIP_LIBS="linux-vdso|ld-linux|libc\.so|libm\.so|libdl\.so|libpthread\.so|librt\.so|libgcc_s|libstdc\+\+|libSDL2|libasound|libudev|libdrm|libwayland|libEGL|libGLES|libMali|libz\.so|libgomp|libvulkan|libmali|libIMGegl|libsrv_um|libusc"

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
