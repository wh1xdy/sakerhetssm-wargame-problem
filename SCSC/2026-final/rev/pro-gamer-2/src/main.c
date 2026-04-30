/* main.c — ROM Bank 0: game loop, input handling, and win screen.
 *
 * The game is a minimal top-down dungeon explorer (Zelda-like).
 * The player can walk freely using the D-pad.  After each move the last
 * SEQ_LEN (8) directions are checked against the encrypted flag: if the
 * decrypted output begins with "CTF{" the win screen is shown.
 *
 * Nothing happens on a wrong sequence (silent failure by design).
 */

#include <gb/gb.h>
#include <gbdk/console.h>
#include <gbdk/font.h>
#include <stdio.h>
#include <stdint.h>

#include "../include/common.h"
#include "../include/checker.h"

/* ── Externals from game_data.c ─────────────────────────────────────────── */
extern const uint8_t BG_TILES[];
extern const uint8_t PLAYER_SPRITE[];
extern const uint8_t MAP_DATA[];
extern uint8_t tile_blocks(uint8_t tx, uint8_t ty);

/* ── Game state (in WRAM, Bank 0 global variables) ───────────────────────── */
static uint8_t player_x;
static uint8_t player_y;
static uint8_t move_history[SEQ_LEN];   /* ring buffer of last SEQ_LEN dirs */
static uint8_t move_head;               /* next-write index (0..SEQ_LEN-1)  */
static uint8_t total_moves;             /* total moves made (capped at 255)  */
static uint8_t game_state;              /* STATE_PLAY or STATE_WIN           */

/* ── Forward declarations ─────────────────────────────────────────────────── */
static void init_game(void);
static void handle_move(int8_t dx, int8_t dy, uint8_t dir);
static void show_win_screen(void);

/* ── Entry point ─────────────────────────────────────────────────────────── */
void main(void) {
    init_game();

    while(game_state == STATE_PLAY) {
        uint8_t keys;
        static uint8_t prev_keys = 0;
        uint8_t new_keys;

        wait_vbl_done();

        keys = joypad();
        new_keys = (uint8_t)(keys & ~prev_keys);

        if(new_keys & J_UP)         handle_move( 0, -1, DIR_N);
        else if(new_keys & J_DOWN)  handle_move( 0, +1, DIR_S);
        else if(new_keys & J_LEFT)  handle_move(-1,  0, DIR_W);
        else if(new_keys & J_RIGHT) handle_move(+1,  0, DIR_E);

        prev_keys = keys;
    }

    show_win_screen();
}

/* ── Initialization ──────────────────────────────────────────────────────── */
static void init_game(void) {
    uint8_t i;

    DISPLAY_OFF;
    SPRITES_8x8;

    /* Load 4 background tiles (floor, wall, pillar, chest) */
    set_bkg_data(0, 4, BG_TILES);

    /* Load player sprite tile */
    set_sprite_data(0, 1, PLAYER_SPRITE);

    /* Write map tilemap to background */
    set_bkg_tiles(0, 0, MAP_W, MAP_H, MAP_DATA);

    /* Place player sprite at spawn position */
    player_x = PLAYER_START_X;
    player_y = PLAYER_START_Y;
    set_sprite_tile(0, 0);
    move_sprite(0,
        (uint8_t)(player_x * 8u + SPR_OFS_X),
        (uint8_t)(player_y * 8u + SPR_OFS_Y));

    /* Clear movement state */
    move_head   = 0;
    total_moves = 0;
    game_state  = STATE_PLAY;
    for(i = 0; i < SEQ_LEN; i++) move_history[i] = DIR_N;

    /* Copy WRAM decrypt template and encrypted flag into WRAM */
    init_wram();

    SHOW_BKG;
    SHOW_SPRITES;
    DISPLAY_ON;
}

/* ── Move handler ────────────────────────────────────────────────────────── */
static void handle_move(int8_t dx, int8_t dy, uint8_t dir) {
    uint8_t new_x = (uint8_t)((int8_t)player_x + dx);
    uint8_t new_y = (uint8_t)((int8_t)player_y + dy);

    /* Blocked by wall, pillar, or chest */
    if(tile_blocks(new_x, new_y)) return;

    player_x = new_x;
    player_y = new_y;
    move_sprite(0,
        (uint8_t)(player_x * 8u + SPR_OFS_X),
        (uint8_t)(player_y * 8u + SPR_OFS_Y));

    /* Record direction in ring buffer */
    move_history[move_head] = dir;
    move_head = (uint8_t)((move_head + 1u) % SEQ_LEN);
    if(total_moves < 255u) total_moves++;

    /* Check sequence once we have at least SEQ_LEN moves */
    if(total_moves >= SEQ_LEN) {
        if(check_sequence(move_history, move_head)) {
            game_state = STATE_WIN;
        }
    }
}

/* ── Win screen ──────────────────────────────────────────────────────────── */
static void show_win_screen(void) {
    uint8_t i;
    uint8_t *flag_bytes = (uint8_t *)WRAM_DEC_FLAG_ADDR;
    char    flag_buf[FLAG_LEN + 1u];

    /* Copy decrypted flag to a null-terminated local buffer */
    for(i = 0; i < FLAG_LEN; i++)
        flag_buf[i] = (char)flag_bytes[i];
    flag_buf[FLAG_LEN] = '\0';

    DISPLAY_OFF;

    /* Re-load font tiles (game tiles are at 0-3; font replaces them) */
    font_init();
    font_load(font_ibm);

    /* Clear screen to spaces, then print */
    cls();

    DISPLAY_ON;

    gotoxy(2, 4);
    printf("*** FLAG FOUND ***");
    gotoxy(1, 8);
    printf("%s", flag_buf);

    /* Halt: wait forever */
    while(1) wait_vbl_done();
}
