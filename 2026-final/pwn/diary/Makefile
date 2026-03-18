CC := gcc
CFLAGS := -Wall -Wextra -O0 -g -fno-stack-protector -no-pie
LDFLAGS :=
TARGET := chall
SRC := chall.c

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET) $(LDFLAGS)

clean:
	rm -f $(TARGET)
