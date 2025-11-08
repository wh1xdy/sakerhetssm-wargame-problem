default: crackme2


crackme2: src/crackme.c src/flag.c src/encrypt-obf2.c
	gcc -Wall -Wpedantic -o $@ $^

test: crackme2
	./crackme2

src/encrypt-obf2.c: src/encrypt-obf.c
	sed "/\/\* BEGIN FUNCTION-DECL main LOC=UNKNOWN \*\//,/\/\* END FUNCTION-DECL main LOC=UNKNOWN \*\//d" src/encrypt-obf.c | \
	sed "/\/\* BEGIN FUNCTION-DEF main LOC=UNKNOWN \*\//,/\/\* END FUNCTION-DEF main LOC=UNKNOWN \*\//d" > src/encrypt-obf2.c

src/encrypt-obf.c: src/encrypt.c
	tigress \
		--Verbosity=1 \
		--Environment=x86_64:Linux:Gcc:5.1 \
		--Transform=Virtualize \
		--Functions=encrypt \
		--out=$@ $<


src/flag.h src/flag.c: src/generate.py
	python3 $< src/flag.h src/flag.c "SSM{b1t_bY_biT_littl3_by_Little}"

clean:
	rm -f crackme2 src/flag.h src/flag.c src/encrypt-obf.c src/encrypt-obf2.c

.PHONY: default test clean
