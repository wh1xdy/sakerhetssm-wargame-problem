#ifndef FLAG_ACCESS_H
#define FLAG_ACCESS_H

#include <stdint.h>

/* Bank 2 — BANKED.
 * Copies FLAG_LEN encrypted flag bytes from ROM bank 2 into dest[].
 * dest must point to a buffer of at least FLAG_LEN bytes (e.g. WRAM_ENC_FLAG_ADDR).
 */
void get_flag_data(uint8_t *dest) BANKED;

#endif /* FLAG_ACCESS_H */
