default: crackme1

crackme1: src/crackme.c src/flag.c
	gcc -Wall -Wpedantic -o $@ $^

test: crackme1
	./crackme1

src/flag.h src/flag.c: src/generate.py
	python3 $< src/flag.h src/flag.c "SSM{k33ping_1t_iN_mY_m3morY}"

clean:
	rm -f crackme1 src/flag.h src/flag.c

.PHONY: default test clean
