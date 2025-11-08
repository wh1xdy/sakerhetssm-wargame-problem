# This Dockerfile builds a kernel and a very basic initramfs with Busybox.
# Run as `docker build --output=custom_system --target=output -f Dockerfile.build_system .`
# The outputs will be in the `custom_system` directory.
FROM debian:bookworm-slim AS build_base

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y install build-essential flex bison bc cpio curl libelf-dev

FROM build_base AS build_fs

# --- INITRAMFS ---
# Download the latest stable version.
RUN mkdir -p /build
WORKDIR /build
RUN curl -sS https://busybox.net/downloads/busybox-1.37.0.tar.bz2 | tar jxf -
WORKDIR /build/busybox-1.37.0
# Build in the default configuration.
RUN make clean && make defconfig && make -j4 install
# Follow the advice printed by `make install`:
# --------------------------------------------------
# You will probably need to make your busybox binary
# setuid root to ensure all configured applets will
# work properly.
# --------------------------------------------------
RUN chmod +s _install/bin/busybox
# Copy the needed libraries from the host system.
RUN for lib in $(ldd _install/bin/busybox | grep -o '/lib[^ ]*'); do cp --parents ${lib} _install/; done
# Copy the init script that will be run on startup.
COPY src/init _install
RUN chmod +x _install/init

FROM build_fs AS build_fs2
ARG FLAG="SSM{placeholder_flag}"
RUN echo ${FLAG} > _install/flag
RUN chmod 400 _install/flag
RUN cd _install && find . -print0 | cpio --create --format=newc --reproducible --null | gzip -c > /build/initramfs.cpio.gz


# --- KERNEL ---
FROM build_base AS build_kernel
WORKDIR /build
RUN curl -sS https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.11.7.tar.xz | tar Jxf -
WORKDIR /build/linux-6.11.7

# Add a barebones config inspired by `make tinyconfig` and https://blog.jm233333.com/linux-kernel/build-and-run-a-tiny-linux-kernel-on-qemu
COPY src/kernel.config kernel/configs/kernel.config

RUN make allnoconfig && make kernel.config && make -j4
# Finally, apply the kernel patch.
COPY src/01-wait4.patch wait4.patch
RUN patch -p1 < wait4.patch
# Build the kernel; the result will be in `arch/x86/boot/bzImage`.
#RUN make allnoconfig && make kernel.config && make -j4
RUN make -j

# --- FINAL OUTPUT ---
FROM scratch AS output
COPY --from=build_fs2 /build/initramfs.cpio.gz /
COPY --from=build_kernel /build/linux-6.11.7/arch/x86/boot/bzImage /
