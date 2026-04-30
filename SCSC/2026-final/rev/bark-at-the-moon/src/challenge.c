#include <stdio.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

#include <sys/types.h>

#include <lua.h>
#include <lualib.h>
#include <lauxlib.h>

#include "bytecode-min.h"
#include "rc4.h"
#include "hex.h"

static int lua_rc4(lua_State *L)
{
    size_t ciphertext_len;
    const unsigned char *ciphertext = (const unsigned char *)lua_tolstring(L, -2, &ciphertext_len);

    size_t key_len;
    const unsigned char *key = (const unsigned char *)lua_tolstring(L, -1, &key_len);

    uint8_t *plaintext = malloc(ciphertext_len);
    RC4(key, key_len, plaintext, ciphertext, ciphertext_len);
    lua_pushlstring(L, (const char *)plaintext, ciphertext_len);
    free(plaintext);

    return 1;
}

static int lua_hexdecode(lua_State *L)
{
    const char *hexstring = luaL_checkstring(L, -1);

    size_t input_len = strlen(hexstring);
    size_t reslen = input_len / 2;
    uint8_t *data = malloc(reslen);
    hexs2bin(hexstring, data);
    lua_pushlstring(L, (const char *)data, reslen);
    free(data);

#ifdef DEBUG
            fprintf(stderr, "hexdecode(%zu) -> %zu\n", input_len, reslen);
#endif

    return 1;
}

int run_program(lua_State *L, char *input)
{
    luaL_openselectedlibs(L, LUA_GLIBK | LUA_COLIBK | LUA_STRLIBK | LUA_UTF8LIBK | LUA_TABLIBK | LUA_MATHLIBK, 0);
    lua_register(L, "crypt", lua_rc4);
    lua_register(L, "hexdecode", lua_hexdecode);

    if (luaL_loadbuffer(L, (char *)bytecode_luac, bytecode_luac_len, "challenge") == LUA_OK)
    {
        lua_pushstring(L, input);
        if (lua_pcall(L, 1, 1, 0) != LUA_OK)
        {
#ifdef DEBUG
            fprintf(stderr, "Error calling Lua: %s\n", lua_tostring(L, -1));
#else
            fprintf(stderr, "A horrible sound is heard\n");
#endif
            return 1;
        }

        int res = lua_toboolean(L, -1);
        lua_pop(L, -1);
        if (res == 1)
        {
            printf("A faint echo can be heard: correct...\n");
            return 0;
        }
        else
        {
            printf("You listen but all you hear is silence\n");
            return 1;
        }
    }
    else
    {
#ifdef DEBUG
        fprintf(stderr, "Error loading Lua: %s\n", lua_tostring(L, -1));
#else
        fprintf(stderr, "The fabric of reality is broken\n");
#endif
        return 1;
    }
}

int main()
{
    printf("Bark at the moon: ");

    char *input = NULL;
    size_t input_len = 0;

    ssize_t input_res = getline(&input, &input_len, stdin);
    if (input_res == -1)
    {
        free(input);
        return 1;
    }

    input[strcspn(input, "\n")] = 0;

    lua_State *L = luaL_newstate();
    int res = run_program(L, input);
    lua_close(L);

    return res;
}
