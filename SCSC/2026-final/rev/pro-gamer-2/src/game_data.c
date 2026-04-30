/* game_data.c — Bank 0: tile graphics and map layout */

#include <gb/gb.h>
#include <stdint.h>
#include "../include/common.h"

/*
 * 8×8 tiles, 2bpp Game Boy format.
 * Each row = 2 bytes: plane0 (low bit), plane1 (high bit).
 * Color = (plane1_bit << 1) | plane0_bit
 *   0 = white, 1 = light gray, 2 = dark gray, 3 = black
 * 16 bytes per tile (8 rows × 2 bytes).
 */
const uint8_t BG_TILES[] = {

    /* Tile 0 — FLOOR: checkerboard of white(0) and light gray(1).
     * Color 1: plane0=1, plane1=0.
     * Row 0: 01010101 → plane0=0x55, plane1=0x00
     * Row 1: 10101010 → plane0=0xAA, plane1=0x00  (alternating) */
    0x55,0x00, 0xAA,0x00,
    0x55,0x00, 0xAA,0x00,
    0x55,0x00, 0xAA,0x00,
    0x55,0x00, 0xAA,0x00,

    /* Tile 1 — WALL: horizontal brick pattern.
     * Color 2 (dark gray): plane0=0, plane1=1.
     * Color 3 (black):     plane0=1, plane1=1.
     * Row 0: mortar (dark gray)  → plane0=0x00, plane1=0xFF
     * Rows 1-3: brick (black)    → plane0=0xFF, plane1=0xFF
     * Row 4: mortar (dark gray)
     * Rows 5-7: brick (black) */
    0x00,0xFF, 0xFF,0xFF,
    0xFF,0xFF, 0xFF,0xFF,
    0x00,0xFF, 0xFF,0xFF,
    0xFF,0xFF, 0xFF,0xFF,

    /* Tile 2 — PILLAR: solid dark, left-edge highlight.
     * Row 0: all dark gray: plane0=0x00, plane1=0xFF
     * Rows 1-6: left pixel dark gray (bit7=0 in plane0), rest black.
     *   plane0=0x7F (01111111), plane1=0xFF
     * Row 7: all dark gray again */
    0x00,0xFF,
    0x7F,0xFF, 0x7F,0xFF,
    0x7F,0xFF, 0x7F,0xFF,
    0x7F,0xFF,
    0x7F,0xFF,
    0x00,0xFF,

    /* Tile 3 — CHEST: black outline, light-gray fill, dark lock hole.
     * Color 1 (light gray): plane0=1, plane1=0.
     * Color 3 (black):      plane0=1, plane1=1.
     * Row 0: all black                → 0xFF, 0xFF
     * Row 1: outer=black, inner=lgray → plane0=0xFF, plane1=0x81
     *   (0x81=10000001 keeps bits 7,0 high → outer pixels black; inner=lgray)
     * Row 2: same as row 1
     * Row 3: lock hole in center pixels 3,4 = dark gray.
     *   plane0=0xE7 (pixels 3,4 are 0), plane1=0x99 (pixels 0,3,4,7 are 1)
     * Rows 4-6: same as row 1
     * Row 7: all black */
    0xFF,0xFF,
    0xFF,0x81, 0xFF,0x81,
    0xE7,0x99,
    0xFF,0x81, 0xFF,0x81,
    0xFF,0x81,
    0xFF,0xFF,
};

/* Player sprite tile (8×8, 2bpp).
 * Color 0 = transparent on sprites.
 * Color 3 (black): both planes = 1.
 *
 * Shape (. = transparent, X = black):
 *   ..XXXX..   0x3C
 *   .XXXXXX.   0x7E
 *   .XXXXXX.   0x7E
 *   .XX..XX.   0x66   (two "eyes")
 *   .XXXXXX.   0x7E
 *   ..XXXX..   0x3C
 *   ...XX...   0x18
 *   ...XX...   0x18   (legs)
 */
const uint8_t PLAYER_SPRITE[] = {
    0x3C,0x3C,
    0x7E,0x7E,
    0x7E,0x7E,
    0x66,0x66,
    0x7E,0x7E,
    0x3C,0x3C,
    0x18,0x18,
    0x18,0x18,
};

/*
 * MAP_DATA — 20×18 flat tile index array (row-major).
 * Indices: 0=floor, 1=wall, 2=pillar, 3=chest
 *
 * Layout (W=wall, .=floor, P=pillar, C=chest):
 *   WWWWWWWWWWWWWWWWWWWW   row 0
 *   W..................W   row 1
 *   W.P...........P....W   row 2
 *   W..................W   row 3
 *   W....WWWW..........W   row 4
 *   W..................W   row 5
 *   W..........WWW.....W   row 6
 *   W...P..............W   row 7
 *   W.......C..........W   row 8  <- player spawns at (9,8)
 *   W..................W   row 9
 *   W...WWWW...........W   row 10
 *   W..................W   row 11
 *   W.............P....W   row 12
 *   W....WWW...........W   row 13
 *   W..................W   row 14
 *   W.P................W   row 15
 *   W..................W   row 16
 *   WWWWWWWWWWWWWWWWWWWW   row 17
 */
const uint8_t MAP_DATA[MAP_H * MAP_W] = {
    /* row 0 */ 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    /* row 1 */ 1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
    /* row 2 */ 1,0,2,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,1,
    /* row 3 */ 1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
    /* row 4 */ 1,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,
    /* row 5 */ 1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
    /* row 6 */ 1,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,1,
    /* row 7 */ 1,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
    /* row 8 */ 1,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,1,
    /* row 9 */ 1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
    /* row10 */ 1,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,
    /* row11 */ 1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
    /* row12 */ 1,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,1,
    /* row13 */ 1,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,
    /* row14 */ 1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
    /* row15 */ 1,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
    /* row16 */ 1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,
    /* row17 */ 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
};

/* Returns non-zero if the tile at (tx, ty) blocks movement. */
uint8_t tile_blocks(uint8_t tx, uint8_t ty) {
    if(tx >= MAP_W || ty >= MAP_H) return 1;
    return MAP_DATA[(uint16_t)ty * MAP_W + tx] != TILE_FLOOR;
}
