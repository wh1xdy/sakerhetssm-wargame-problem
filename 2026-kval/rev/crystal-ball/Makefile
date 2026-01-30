
crystal-ball: crystal-ball.cpp keygen.hpp
	clang++ -O0 -ftemplate-depth=10240 -o $@ crystal-ball.cpp

crystal-ball-dev: crystal-ball.cpp keygen.hpp
	clang++ -O0 -ftemplate-depth=10240 -DDEBUG -o $@ crystal-ball.cpp

keygen: keygen.cpp keygen.hpp
	clang++ -O2 -ftemplate-depth=10240 -o $@ keygen.cpp

clean:
	rm -rf crystal-ball crystal-ball-dev keygen
