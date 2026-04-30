CC = gcc
CFLAGS = -no-pie -fno-pie -g

all: a.out a.out.patched

a.out: main.c
	$(CC) $(CFLAGS) -o a.out main.c

a.out.patched: a.out libc.so.6 ld-linux-x86-64.so.2
	cp a.out a.out.patched
	patchelf --set-interpreter ./ld-linux-x86-64.so.2 --set-rpath . a.out.patched

docker-build: a.out
	docker build -t jmid2 .

docker-run:
	docker run -p 1337:1337 jmid2

clean:
	rm -f a.out a.out.patched
