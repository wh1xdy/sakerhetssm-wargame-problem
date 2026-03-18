
C_MODULES=modules/module1.c modules/module2.c modules/module3.c modules/module4.c modules/module5.c modules/module6.c modules/module7.c modules/module8.c
CWASM_MODULES=modules/module1.cwasm modules/module2.cwasm modules/module3.cwasm modules/module4.cwasm modules/module5.cwasm modules/module6.cwasm modules/module7.cwasm modules/module8.cwasm

build/fragmented: $(CWASM_MODULES)
	mkdir -p build
	RUSTFLAGS="-Zlocation-detail=none" cargo build -Z unstable-options --release --artifact-dir build

run: $(CWASM_MODULES)
	cargo run


toolchain:
	wget https://apt.llvm.org/llvm.sh
	chmod +x llvm.sh
	sudo ./llvm.sh 20

generator: generator.c $(C_MODULES)
	clang -o $@ $^

modules/%.cwasm: modules/%.wasm
	wasmtime compile \
		-W gc=n \
		-W gc-support=n \
		-W component-model=n \
		-W bulk-memory=n \
		-W multi-memory=n \
		-W threads=n \
		-W reference-types=n \
		-o $@ $<

modules/%.wasm: modules/%.c
	clang \
		--target=wasm32 \
		-nostdlib \
		-Wl,--no-entry \
		-Wl,--export-all \
		-o $@ $^

clean:
	rm -rf generator build/fragmented modules/*.wasm modules/*.cwasm

.PHONY: build/fragmented clean run
