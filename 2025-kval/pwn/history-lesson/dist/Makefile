default: run-dist

run-dist: history-lesson.hash
	docker run --security-opt apparmor=unconfined --privileged --rm -it -p31337:31337 history-lesson:latest

run-custom: history-lesson-custom.hash
	docker run --security-opt apparmor=unconfined --privileged --rm -it -p31337:31337 history-lesson-custom:latest

history-lesson.hash: Dockerfile build/bzImage build/initramfs-dist.cpio.gz
	docker buildx build --build-arg "INITRAMFS=initramfs-dist.cpio.gz" --iidfile $@ -t history-lesson -f $< .

history-lesson-custom.hash: Dockerfile build/bzImage build/initramfs.cpio.gz
	docker buildx build --build-arg "INITRAMFS=initramfs.cpio.gz" --iidfile $@ -t history-lesson-custom -f $< .

build/bzImage build/initramfs.cpio.gz: kernel.Dockerfile src/init src/run.sh src/01-wait4.patch src/kernel.config
	docker buildx build --output=build --target=output -f kernel.Dockerfile .
	touch build/bzImage build/initramfs.cpio.gz

.PHONY: default run-dist run-custom
