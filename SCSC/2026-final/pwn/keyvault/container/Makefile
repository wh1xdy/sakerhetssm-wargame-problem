CC = gcc
CFLAGS = -Wall -pie -fPIE -fstack-protector-all
LDFLAGS = -pie -Wl,-z,relro,-z,now

all: keyvault

keyvault: main.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f keyvault

.PHONY: all clean
