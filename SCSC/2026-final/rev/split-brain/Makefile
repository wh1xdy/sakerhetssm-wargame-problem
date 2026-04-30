
build/split-brain: programs/flag_checker.bin
	mkdir -p build
	RUSTFLAGS="-Zlocation-detail=none -Zfmt-debug=none" cargo build -Z unstable-options --release --artifact-dir build --features embed_challenge

programs/%.bin: programs/%.asm
	python3 assembler.py $< $@

clean:
	rm -rf build/split-brain programs/*.bin

.PHONY: build/split-brain clean
