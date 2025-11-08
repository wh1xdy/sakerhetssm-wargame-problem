default: build

test: history-lesson-server.hash
	docker run --security-opt apparmor=unconfined --privileged --rm -it -p31337:31337 history-lesson-server:latest

run-qemu:
	qemu-system-x86_64 \
		-initrd custom_system/initramfs.cpio.gz \
		-kernel custom_system/bzImage \
		-append "root=/dev/ram console=ttyS0 oops=panic quiet" \
		-nographic \
		-monitor /dev/null \
		-m 256 \
		-smp 1 \
		-no-reboot

update-patch:
	git -C linux diff > src/01-wait4.patch

build/bzImage build/initramfs-dist.cpio.gz build/initramfs-server.cpio.gz: kernel.Dockerfile src/init src/run.sh src/01-wait4.patch src/kernel.config
	docker buildx build --output=build --target=output -f kernel.Dockerfile .
	touch build/bzImage build/initramfs.cpio.gz
	mv build/initramfs.cpio.gz build/initramfs-dist.cpio.gz
	
	docker buildx build --build-arg "FLAG=SSM{1t_w4s_3ven_M0re_SubTle_b4ck_th3n}" --output=build --target=output -f kernel.Dockerfile .
	touch build/bzImage build/initramfs.cpio.gz
	mv build/initramfs.cpio.gz build/initramfs-server.cpio.gz

history-lesson-server.hash: Dockerfile build/bzImage build/initramfs-server.cpio.gz
	docker buildx build --iidfile $@ -t history-lesson-server -f $< .

history-lesson.hash: Dockerfile build/bzImage build/initramfs-dist.cpio.gz
	docker buildx build --build-arg "INITRAMFS=initramfs-dist.cpio.gz" --iidfile $@ -t history-lesson -f $< .

linux:
	git clone --depth=1 --branch v6.11.7 https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# Useful commands:
# linux/scripts/extract-vmlinux build/bzImage > build/vmlinux
# zcat initramfs-dist.cpio.gz | cpio -idmv --no-absolute-filenames
# zcat initramfs-server.cpio.gz | cpio -idmv --no-absolute-filenames

.PHONY: default test run-qemu build build-debug update-patch
