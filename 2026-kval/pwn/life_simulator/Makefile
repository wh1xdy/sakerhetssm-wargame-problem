test: solve.sh container/life_simulator
	./$<

container/life_simulator: life_simulator.c
	gcc -O0 -o $@ $<

.PHONY: test
