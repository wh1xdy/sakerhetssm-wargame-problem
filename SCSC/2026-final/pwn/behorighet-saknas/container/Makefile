CC=gcc
CFLAGS=-fno-stack-protector -z execstack -no-pie -Og -g
LIBS=-lcrypto
TARGET=service
SOURCE=challenge.c

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) -static -o $(TARGET) $(SOURCE) $(LIBS)

clean:
	rm -f $(TARGET)
