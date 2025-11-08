default: exploit

exploit: exploit.c
	musl-gcc -o $@ -static -Os $^

clean:
	rm -rf exploit

.PHONY: default clean
