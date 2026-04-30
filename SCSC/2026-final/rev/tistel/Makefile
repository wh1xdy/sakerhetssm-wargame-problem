
CC ?= clang
PY ?= python3
CFLAGS := -Wall -Wextra -Wpedantic # -O2

challenge: dist/challenge

dist/challenge: src/challenge.c src/target.h | dist
	$(CC) $(CFLAGS) -o $@ src/challenge.c
	llvm-strip -s $@ || strip -s $@

dist:
	mkdir -p dist || mkdir dist

src/target.h: src/generate.py
	$(PY) src/generate.py > src/target.h

clean:
	rm -rf dist || rmdir /s /q dist
	rm -f src/target.h || del src\target.h

.PHONY: clean
