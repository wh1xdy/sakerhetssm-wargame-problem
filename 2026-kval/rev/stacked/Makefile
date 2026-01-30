
challenge: challenge.c program.c
	clang -s -O0 -o $@ $^

challenge-dev: challenge.c program.c
	clang -s -O0 -o $@ -DDEBUG $^

program.h program.c: generate.py
	python3 generate.py 'SSM{stack_em_h1gh}' 1337

clean:
	rm -rf challenge challenge-dev

.PHONY: clean