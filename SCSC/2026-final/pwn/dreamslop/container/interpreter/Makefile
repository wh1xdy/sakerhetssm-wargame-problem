CC      ?= cc
CFLAGS  ?= -std=c11 -D_POSIX_C_SOURCE=200809L -Wall -Wextra -Wpedantic -O2 -g -Iinclude -MMD -MP
LDFLAGS ?= -lm

SRC := $(wildcard src/*.c)
OBJ := $(SRC:src/%.c=build/%.o)
DEP := $(OBJ:.o=.d)
BIN := dreamslop

-include $(DEP)

.PHONY: all clean test run

all: $(BIN)

$(BIN): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $(OBJ) $(LDFLAGS)

build/%.o: src/%.c
	@mkdir -p build
	$(CC) $(CFLAGS) -c -o $@ $<

test: $(BIN)
	@bash tests/run_tests.sh

run: $(BIN)
	@./$(BIN)

clean:
	rm -rf build $(BIN)
