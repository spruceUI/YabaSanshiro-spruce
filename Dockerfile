FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Configure multiarch for arm64 cross-compilation (glibc 2.31)
RUN dpkg --add-architecture arm64 && \
    sed -i 's/^deb http/deb [arch=amd64] http/g' /etc/apt/sources.list && \
    echo "deb [arch=arm64] http://ports.ubuntu.com/ubuntu-ports focal main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb [arch=arm64] http://ports.ubuntu.com/ubuntu-ports focal-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    apt-transport-https \
    gnupg \
    software-properties-common \
    && wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | apt-key add - && \
    apt-add-repository 'deb https://apt.kitware.com/ubuntu/ focal main' && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    cmake \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu \
    pkg-config \
    git \
    ca-certificates \
    ccache \
    python3 \
    # arm64 cross-compile dependencies
    libsdl2-dev:arm64 \
    libasound2-dev:arm64 \
    libpulse-dev:arm64 \
    zlib1g-dev:arm64 \
    libudev-dev:arm64 \
    libgles2-mesa-dev:arm64 \
    libegl1-mesa-dev:arm64 \
    libopenal-dev:arm64 \
    libboost-filesystem-dev:arm64 \
    libboost-system-dev:arm64 \
    libboost-locale-dev:arm64 \
    libboost-date-time-dev:arm64 \
    libboost-thread-dev:arm64 \
    libpng-dev:arm64 \
    libglew-dev:arm64 \
    freeglut3-dev:arm64 \
    libssl-dev:arm64 \
    libvulkan-dev:arm64 \
    && rm -rf /var/lib/apt/lists/*

COPY build.sh /build.sh
RUN chmod +x /build.sh
COPY patches/ /patches/

WORKDIR /build
ENTRYPOINT ["/build.sh"]
