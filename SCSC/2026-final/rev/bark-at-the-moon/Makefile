
challenge-dbg: lua-5.5.0/src/liblua.a src/challenge.c src/rc4.c src/hex.c src/bytecode.h
	clang -DDEBUG -Wall -O2 -s -Ilua-5.5.0/src/ -lm -o $@ src/challenge.c src/rc4.c src/hex.c lua-5.5.0/src/liblua.a

challenge: lua-5.5.0/src/liblua.a src/challenge.c src/rc4.c src/hex.c src/bytecode-min.h
	clang -Wall -O2 -s -Ilua-5.5.0/src/ -lm -o $@ src/challenge.c src/rc4.c src/hex.c lua-5.5.0/src/liblua.a

node_modules/luamin/bin/luamin:
	pnpm install luamin

src/bytecode-min.h: src/challenge.min.luac
	xxd -n bytecode_luac -i $< > $@

src/bytecode.h: src/challenge.luac
	xxd -n bytecode_luac -i $< > $@

src/challenge.min.luac: src/challenge.min.lua
	lua-5.5.0/src/luac -o $@ $<

src/challenge.min.lua: node_modules/luamin/bin/luamin src/challenge.lua
	node_modules/luamin/bin/luamin --file src/challenge.lua > src/challenge.min.lua

src/challenge.luac: src/challenge.lua
	lua-5.5.0/src/luac -o $@ $<

lua-5.5.0/src/luac lua-5.5.0/src/liblua.a: lua-5.5.0
	make -C lua-5.5.0

lua-5.5.0/Makefile: lua-5.5.0.tar.gz
	tar zxf lua-5.5.0.tar.gz

lua-5.5.0.tar.gz:
	curl -L -R -O https://www.lua.org/ftp/lua-5.5.0.tar.gz

clean:
	rm -f challenge-dbg challenge src/challenge.luac src/bytecode.h

.PHONY: clean
