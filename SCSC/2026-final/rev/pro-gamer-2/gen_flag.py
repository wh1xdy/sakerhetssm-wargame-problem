#!/usr/bin/env python3
"""
gen_flag.py — CTF Game Boy challenge flag generator

Usage:
    python gen_flag.py --flag "YOUR_FLAG_HERE" --seq "NESWNESW"
                       [--magic-prefix N]   # how many flag bytes stored as plaintext in bank1 (default 4)
                       [--no-verify]        # skip uniqueness exhaustive check

    --flag   Printable ASCII string, any length ≤ 49 characters
             (limit keeps the WRAM routine below the $C200 boundary)
    --seq    Sequence of N/E/S/W characters, any length 1–16
    --magic-prefix N  (default 4): first N bytes of the flag are stored as plaintext
             in bank 1 as a fast pre-filter.  The reverser will see them there.

Outputs (in include/):
    flag_data.h      — ENC_FLAG[], FLAG_LEN, SEQ_LEN, WRAM layout constants,
                       fingerprint constants (STORED_FP_*), FLAG_MAGIC constants
    wram_template.h  — wram_template[] SM83 bytecode for the self-modifying WRAM routine

Key derivation (must stay in sync with src/checker.c):
    dir_val: N=0, E=1, S=2, W=3
    derive_key(step, dir_val) = (((dir_val + 1) * 0x5D) ^ (step * 0x37) ^ 0xAB) & 0xFF

Encryption:
    enc[i] = flag_byte[i] ^ derive_key(i % SEQ_LEN, seq_dir_val[i % SEQ_LEN])

Uniqueness guarantee (two-part check in check_sequence()):
    1. Plausibility: decrypted bytes 0..FLAG_MAGIC_LEN-1 == FLAG_MAGIC[]  (bank 1)
    2. Bijective fingerprint: base4_encode(input_seq) matches STORED_FP_* (bank 1)
       STORED_FP = base4_encode(correct_seq) XOR obfuscation
       obfuscation = ENC_FLAG[0] ^ ENC_FLAG[FLAG_LEN-1]
"""

import argparse
import os
import sys
from itertools import product as itertools_product

# ── Constants ────────────────────────────────────────────────────────────────

DIR_VAL = {'N': 0, 'E': 1, 'S': 2, 'W': 3}
MAX_FLAG_LEN = 49   # WRAM_ROUTINE_SIZE ≤ 0xC200 - 0xC100 = 256  →  (256-7)/5 = 49
MAX_SEQ_LEN  = 16   # fingerprint fits in uint32_t (16 * 2 = 32 bits)
WRAM_ROUTINE_ADDR = 0xC100

INCLUDE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "include")


# ── Key derivation ────────────────────────────────────────────────────────────

def derive_key(step: int, dir_val: int) -> int:
    """Must stay in sync with checker.c."""
    return (((dir_val + 1) * 0x5D) ^ (step * 0x37) ^ 0xAB) & 0xFF


def encrypt_flag(flag_bytes: bytes, seq: str) -> list[int]:
    seq_len = len(seq)
    seq_vals = [DIR_VAL[c] for c in seq]
    return [b ^ derive_key(i % seq_len, seq_vals[i % seq_len])
            for i, b in enumerate(flag_bytes)]


# ── Fingerprint ───────────────────────────────────────────────────────────────

def base4_encode(seq: str) -> int:
    """Bijective base-4 encoding of a direction sequence.
       Returns an integer; different sequences always produce different values."""
    result = 0
    for i, c in enumerate(seq):
        result |= DIR_VAL[c] << (2 * i)
    return result


def compute_fingerprint_bytes(seq: str, enc_flag: list[int]) -> tuple[int, int, int, int]:
    """Return (obfusc, STORED_FP_0, STORED_FP_1, STORED_FP_2, STORED_FP_3)."""
    fp     = base4_encode(seq)
    obfusc = enc_flag[0] ^ enc_flag[-1]
    fp0    = (fp & 0xFF)        ^ obfusc
    fp1    = ((fp >> 8) & 0xFF) ^ obfusc
    fp2    = ((fp >> 16) & 0xFF) ^ obfusc
    fp3    = ((fp >> 24) & 0xFF) ^ obfusc
    return obfusc, fp0, fp1, fp2, fp3


# ── Uniqueness verification ───────────────────────────────────────────────────

def check_valid(dec: bytes, flag_magic: bytes) -> bool:
    """Same two-part logic as check_sequence() in checker.c."""
    return dec[:len(flag_magic)] == flag_magic


def verify_unique(enc: list[int], seq: str, flag_magic: bytes,
                  enc_flag_first: int, enc_flag_last: int) -> int:
    """Return number of sequences that pass the FULL validation (magic + fingerprint).
    With the fingerprint check this should always be exactly 1."""
    flag_len = len(enc)
    seq_len  = len(seq)
    obfusc   = enc_flag_first ^ enc_flag_last
    correct_fp = base4_encode(seq)

    matches = 0
    for candidate in itertools_product(DIR_VAL.keys(), repeat=seq_len):
        # Decrypt with candidate sequence
        dec = bytes([enc[i] ^ derive_key(i % seq_len, DIR_VAL[candidate[i % seq_len]])
                     for i in range(flag_len)])
        if not check_valid(dec, flag_magic):
            continue
        # Fingerprint check — all four bytes must match
        cand_fp = base4_encode(''.join(candidate))
        if cand_fp != correct_fp:
            # Different sequences always differ in fingerprint (bijection)
            continue
        # All parts match → this is a valid solution
        matches += 1

    return matches


# ── WRAM template generator ───────────────────────────────────────────────────

def build_wram_template(flag_len: int, enc_addr: int, dec_addr: int) -> list[int]:
    """Build the SM83 bytecode template.
    Layout: LD HL,enc_addr | LD DE,dec_addr | (LD A,(HL+); XOR $00; LD (DE),A; INC DE) × flag_len | RET
    """
    enc_lo = enc_addr & 0xFF
    enc_hi = (enc_addr >> 8) & 0xFF
    dec_lo = dec_addr & 0xFF
    dec_hi = (dec_addr >> 8) & 0xFF
    tmpl = [
        0x21, enc_lo, enc_hi,   # LD HL, enc_addr
        0x11, dec_lo, dec_hi,   # LD DE, dec_addr
    ]
    for _ in range(flag_len):
        tmpl += [0x2A, 0xEE, 0x00, 0x12, 0x13]
    tmpl += [0xC9]  # RET
    return tmpl


# ── Code generators ───────────────────────────────────────────────────────────

def write_flag_data_h(flag_str: str, seq: str, enc: list[int],
                      magic_prefix: int,
                      enc_addr: int, dec_addr: int,
                      routine_size: int) -> None:
    flag_len  = len(flag_str)
    seq_len   = len(seq)
    flag_bytes = flag_str.encode('ascii')

    _, fp0, fp1, fp2, fp3 = compute_fingerprint_bytes(seq, enc)

    magic_bytes = flag_bytes[:magic_prefix]
    magic_hex   = ', '.join(f'0x{b:02X}' for b in magic_bytes)

    # flag_data.h — included by common.h (all TUs).
    # ENC_FLAG is declared extern here; defined in enc_flag_data.h (bank 2 only).
    content = f"""\
/* AUTO-GENERATED by gen_flag.py — DO NOT EDIT */
/* Re-generate with: python gen_flag.py --flag "..." --seq "..." */
#ifndef FLAG_DATA_H
#define FLAG_DATA_H

/* ── Sizes ────────────────────────────────────────────────────────────── */
#define FLAG_LEN         {flag_len}
#define SEQ_LEN          {seq_len}
#define FLAG_MAGIC_LEN   {magic_prefix}

/* ── WRAM layout ──────────────────────────────────────────────────────── */
#define WRAM_ROUTINE_ADDR    0x{WRAM_ROUTINE_ADDR:04X}
#define WRAM_ROUTINE_SIZE    {routine_size}
#define WRAM_ENC_FLAG_ADDR   0x{enc_addr:04X}
#define WRAM_DEC_FLAG_ADDR   0x{dec_addr:04X}

/* ── Encrypted flag — extern declaration (definition in enc_flag_data.h) */
extern const uint8_t ENC_FLAG[{flag_len}];

/* First and last encrypted bytes — used for fingerprint obfuscation */
#define ENC_FLAG_FIRST  0x{enc[0]:02X}
#define ENC_FLAG_LAST   0x{enc[-1]:02X}

/* ── Fingerprint verification constants (ROM bank 1) ─────────────────── *
 * Stored as: STORED_FP_i = (base4_encode(correct_seq) byte i) ^ (ENC_FLAG_FIRST ^ ENC_FLAG_LAST)
 * The check_sequence() function computes base4_encode(input_seq), applies the
 * same obfuscation, and compares to these values.  The bijection guarantees
 * exactly one sequence produces a match.
 */
#define STORED_FP_0     0x{fp0:02X}
#define STORED_FP_1     0x{fp1:02X}
#define STORED_FP_2     0x{fp2:02X}
#define STORED_FP_3     0x{fp3:02X}

/* ── Flag magic prefix (ROM bank 1) — plaintext pre-filter ───────────── *
 * First {magic_prefix} bytes of the flag stored in bank 1 as a fast pre-check
 * before the more expensive fingerprint comparison.  Intentionally visible to
 * a reverser as a clue, but knowing the prefix does not reveal the sequence.
 */
static const uint8_t FLAG_MAGIC[FLAG_MAGIC_LEN] = {{
    {magic_hex}
}};

#endif /* FLAG_DATA_H */
"""
    out_path = os.path.join(INCLUDE_DIR, "flag_data.h")
    with open(out_path, 'w') as f:
        f.write(content)
    print(f"[ok] Wrote {out_path}")


def write_enc_flag_data_h(enc: list[int]) -> None:
    """Write the ENC_FLAG array definition — included ONLY by flag_data.c (bank 2)."""
    enc_hex = ', '.join(f'0x{b:02X}' for b in enc)
    content = f"""\
/* AUTO-GENERATED by gen_flag.py — DO NOT EDIT */
/* Include ONLY from flag_data.c (ROM bank 2). */
#ifndef ENC_FLAG_DATA_H
#define ENC_FLAG_DATA_H

const uint8_t ENC_FLAG[{len(enc)}] = {{
    {enc_hex}
}};

#endif /* ENC_FLAG_DATA_H */
"""
    out_path = os.path.join(INCLUDE_DIR, "enc_flag_data.h")
    with open(out_path, 'w') as f:
        f.write(content)
    print(f"[ok] Wrote {out_path}")


def write_wram_template_h(flag_len: int, enc_addr: int, dec_addr: int) -> None:
    tmpl = build_wram_template(flag_len, enc_addr, dec_addr)
    routine_size = len(tmpl)
    hex_rows = []
    for i, b in enumerate(tmpl):
        comment = ""
        if i == 0:
            comment = f"  /* LD HL, ${enc_addr:04X} (enc-flag buffer) */"
        elif i == 3:
            comment = f"  /* LD DE, ${dec_addr:04X} (dec-output buffer) */"
        elif i >= 6 and (i - 6) % 5 == 0:
            fb = (i - 6) // 5
            comment = f"  /* flag byte {fb} */"
        elif i == routine_size - 1:
            comment = "  /* RET */"
        hex_rows.append(f"    0x{b:02X},{comment}")

    body = "\n".join(hex_rows)
    content = f"""\
/* AUTO-GENERATED by gen_flag.py — DO NOT EDIT */
/* WRAM self-modifying decrypt routine template.
 * Placed in ROM bank 1 (checker.c has #pragma bank 1).
 * Copied to WRAM at runtime; XOR key bytes (0x00 placeholders) are
 * patched by patch_wram() before each sequence check.
 *
 * Structure:
 *   Preamble (6 bytes):  LD HL, enc_addr ; LD DE, dec_addr
 *   Body ({flag_len}x5 = {flag_len*5} bytes): LD A,(HL+) ; XOR $00 ; LD (DE),A ; INC DE
 *   Trailer (1 byte):   RET
 *   Total: {routine_size} bytes
 */
#ifndef WRAM_TEMPLATE_H
#define WRAM_TEMPLATE_H

static const uint8_t wram_template[WRAM_ROUTINE_SIZE] = {{
{body}
}};

#endif /* WRAM_TEMPLATE_H */
"""
    out_path = os.path.join(INCLUDE_DIR, "wram_template.h")
    with open(out_path, 'w') as f:
        f.write(content)
    print(f"[ok] Wrote {out_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="GB CTF challenge flag generator")
    parser.add_argument("--flag",         required=True)
    parser.add_argument("--seq",          required=True)
    parser.add_argument("--magic-prefix", type=int, default=4,
                        help="Number of plaintext flag bytes embedded as bank-1 pre-filter (default 4)")
    parser.add_argument("--no-verify",    action="store_true",
                        help="Skip exhaustive uniqueness check (fast, use for large SEQ_LEN)")
    args = parser.parse_args()

    flag_str      = args.flag
    seq           = args.seq.upper()
    magic_prefix  = args.magic_prefix

    flag_len  = len(flag_str)
    seq_len   = len(seq)

    # ── Validate inputs ────────────────────────────────────────────────────
    if flag_len < 1:
        sys.exit("Error: flag must be non-empty")
    if flag_len > MAX_FLAG_LEN:
        sys.exit(f"Error: flag length {flag_len} exceeds maximum {MAX_FLAG_LEN} "
                 f"(WRAM routine would overflow $C200 boundary)")
    if not all(32 <= ord(c) < 127 for c in flag_str):
        sys.exit("Error: flag must contain only printable ASCII characters")
    if seq_len < 1:
        sys.exit("Error: sequence must be non-empty")
    if seq_len > MAX_SEQ_LEN:
        sys.exit(f"Error: sequence length {seq_len} exceeds maximum {MAX_SEQ_LEN}")
    if not all(c in DIR_VAL for c in seq):
        sys.exit(f"Error: sequence must only contain N, E, S, W (got {seq!r})")
    if magic_prefix < 1 or magic_prefix > flag_len:
        sys.exit(f"Error: --magic-prefix must be 1..{flag_len}")

    # ── Compute WRAM layout ────────────────────────────────────────────────
    routine_size    = 6 + flag_len * 5 + 1
    # Align enc_flag start to next 16-byte boundary above end of routine
    enc_addr_raw    = WRAM_ROUTINE_ADDR + routine_size
    enc_addr        = (enc_addr_raw + 15) & ~15
    dec_addr        = enc_addr + flag_len

    # Sanity: everything fits in WRAM (< $E000)
    wram_end = dec_addr + flag_len
    if wram_end > 0xE000:
        sys.exit(f"Error: WRAM layout overflows: dec_end=0x{wram_end:04X}")

    # ── Encrypt flag ───────────────────────────────────────────────────────
    flag_bytes = flag_str.encode('ascii')
    enc = encrypt_flag(flag_bytes, seq)

    # ── Verify uniqueness ──────────────────────────────────────────────────
    flag_magic = flag_bytes[:magic_prefix]
    if not args.no_verify:
        if seq_len > 10:
            print(f"[info] SEQ_LEN={seq_len} → 4^{seq_len}={4**seq_len} candidates; "
                  f"verification may take a moment...")
        n = verify_unique(enc, seq, flag_magic, enc[0], enc[-1])
        if n == 1:
            print(f"[ok] Unique solution confirmed: {seq}")
        else:
            print(f"[warn] {n} sequences pass full validation. "
                  f"This should never happen with the fingerprint check enabled.")
    else:
        print(f"[skip] Uniqueness check skipped (--no-verify)")

    # ── Write generated files ──────────────────────────────────────────────
    write_flag_data_h(flag_str, seq, enc, magic_prefix, enc_addr, dec_addr, routine_size)
    write_enc_flag_data_h(enc)
    write_wram_template_h(flag_len, enc_addr, dec_addr)

    print(f"     Flag length  : {flag_len} bytes")
    print(f"     Seq length   : {seq_len} steps")
    print(f"     Magic prefix : {magic_prefix} bytes ({flag_magic!r})")
    print(f"     WRAM layout  : routine=${WRAM_ROUTINE_ADDR:04X}..${WRAM_ROUTINE_ADDR+routine_size-1:04X}"
          f"  enc=${enc_addr:04X}  dec=${dec_addr:04X}")
    print(f"     Sequence     : {seq}  (keep secret!)")


if __name__ == "__main__":
    main()
