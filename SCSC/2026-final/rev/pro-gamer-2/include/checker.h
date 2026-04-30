#ifndef CHECKER_H
#define CHECKER_H

#include <stdint.h>

/*
 * Bank 1 — BANKED functions.
 *
 * init_wram():
 *   Copies the wram_template (SM83 bytecode) to WRAM_ROUTINE_ADDR ($C100).
 *   Also copies the encrypted flag bytes from Bank 2 to WRAM_ENC_FLAG_ADDR ($C200).
 *   Called once at startup from main().
 *
 * reset_wram():
 *   Re-copies only the template to $C100 (zeros out the XOR key slots),
 *   restoring a "clean" routine ready for a new patch cycle.
 *   Called before each sequence check attempt.
 *
 * patch_wram(step, dir):
 *   Computes derive_key(step, dir) and writes it into the three XOR-immediate
 *   bytes in the WRAM routine that correspond to flag bytes at positions
 *   step, step+8, step+16.
 *   Called once per recorded move (step = 0..SEQ_LEN-1).
 *
 * check_sequence(move_history, head):
 *   Orchestrates reset_wram + patch_wram for all 8 slots, then calls the
 *   WRAM routine.  Returns 1 if the first 4 bytes of the decrypted output
 *   match "CTF{", 0 otherwise.
 *   move_history is a SEQ_LEN-element ring buffer; head is the write index.
 */

void init_wram(void) BANKED;
void reset_wram(void) BANKED;
void patch_wram(uint8_t step, uint8_t dir) BANKED;
uint8_t check_sequence(uint8_t *move_history, uint8_t head) BANKED;

#endif /* CHECKER_H */
