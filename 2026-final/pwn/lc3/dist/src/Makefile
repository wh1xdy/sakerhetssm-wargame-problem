CC      = cc
CFLAGS  = -Wall -Wextra -O2 -std=c11
LDFLAGS = -Wl,-T,lc3.ld,-z,norelro
TARGET  = lc3emu
SRCS    = main.c emu.c
OBJS    = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS) lc3.ld
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $(OBJS)

%.o: %.c emu.h
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean
