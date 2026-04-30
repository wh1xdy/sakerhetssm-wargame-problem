/* flag_data.c — ROM Bank 2 (BANKED): encrypted flag storage + accessor.
 *
 * ENC_FLAG[] is defined in the auto-generated include/flag_data.h.
 * Run: python gen_flag.py --flag "..." --seq "..." to regenerate it.
 *
 * get_flag_data(dest) copies FLAG_LEN bytes from ENC_FLAG into dest[].
 * Callers must ensure dest has room for FLAG_LEN bytes.
 */

#pragma bank 2

#include <stdint.h>
#include "../include/common.h"
#include "../include/flag_access.h"
#include "../include/enc_flag_data.h"  /* AUTO-GENERATED: defines ENC_FLAG[] (bank 2 only) */

void get_flag_data(uint8_t *dest) BANKED {
    uint8_t i;
    for(i = 0; i < FLAG_LEN; i++)
        dest[i] = ENC_FLAG[i];
}
