#!/usr/bin/env python3
import sys
import re
# Based on ARCHITECTURE.md for Ring-16 v5

OPCODES = {
    "SYS": 0x0, "MOV": 0x1, "LDI": 0x2, "LUI": 0x3, "LDM": 0x4, "STM": 0x5,
    "PUSH": 0x6, "POP": 0x7, "ADD": 0x8, "SUB": 0x9, "CMP": 0xA, "MUL": 0xB,
    "OR": 0xC, "XOR": 0xD, "SHL": 0xE, "BRANCH": 0xF,
    # Pseudo-instructions
    "CALL": 0xFF, "RET": 0xFF,
}

SYS_SUBOPS = {
    "NOP": 0x00, "HALT": 0x01, "PUTC": 0x02, "GETC": 0x03, "CHECK": 0x42,
}

BRANCH_CONDS = {
    "EQ": 0x0, "Z": 0x0, "NE": 0x1, "NZ": 0x1, "CS": 0x2, "C": 0x2,
    "CC": 0x3, "NC": 0x3, "OS": 0x4, "OC": 0x5, "GT": 0x6, "LE": 0x7,
    "AL": 0xD, "CALL": 0xE, "JREG": 0xF,
}

REGISTERS = {f"R{i}": i for i in range(16)}
REGISTERS.update({f"r{i}": i for i in range(16)})
REGISTERS.update({"LR": 14, "lr": 14, "R14": 14, "r14": 14, "R13": 13, "r13": 13})
REGISTERS.update({"SP": 15, "sp": 15, "R15": 15, "r15": 15})

class AssemblerError(Exception):
    pass

def parse_operand(op, labels, current_address):
    """Parses an operand string into a numerical value."""
    op = op.strip()
    if not op:
        raise AssemblerError("Empty operand.")

    # Register
    if op.upper() in REGISTERS:
        return REGISTERS[op.upper()]

    # Label
    if op in labels:
        return labels[op]

    # Immediate value
    try:
        if op.lower().startswith('0x'):
            return int(op, 16)
        return int(op)
    except ValueError:
        raise AssemblerError(f"Invalid operand: '{op}' is not a valid register, label, or number.")

def scramble_instruction(opcode, rd, imm8):
    """
    Scrambles a logical instruction into its physical binary format.
    Logical Layout:  [Opcode: 4] [Dest: 4] [Src/Imm: 8]
    Physical Layout: [Imm_Low: 4] [Dest: 4] [Opcode: 4] [Imm_High: 4]
    """
    if not (0 <= opcode <= 0xF and 0 <= rd <= 0xF and 0 <= imm8 <= 0xFF):
        raise AssemblerError("Invalid instruction components for scrambling.")

    imm_high = (imm8 >> 4) & 0xF
    imm_low = imm8 & 0xF

    # Reconstruct into physical layout
    physical_word = (imm_low << 12) | (rd << 8) | (opcode << 4) | imm_high
    return physical_word

def assemble_line(line, labels, current_address):
    """Assembles a single line of assembly code into a 16-bit integer or list of integers."""
    parts = re.split(r'[\s,]+', line.strip(), maxsplit=1)
    mnemonic = parts[0].upper()

    if mnemonic not in OPCODES:
        raise AssemblerError(f"Unknown mnemonic: {mnemonic}")

    opcode = OPCODES[mnemonic]
    operands_str = parts[1] if len(parts) > 1 else ""
    operands = [op.strip() for op in operands_str.split(',') if op.strip()]

    rd, rs, imm8, imm4 = 0, 0, 0, 0

    # Instruction-specific parsing
    if mnemonic == "SYS":
        # SYS Imm8
        if len(operands) != 1:
            raise AssemblerError(f"SYS expects 1 operand, got {len(operands)}")
        sub_op_str = operands[0].upper()
        if sub_op_str in SYS_SUBOPS:
            imm8 = SYS_SUBOPS[sub_op_str]
        else:
            imm8 = parse_operand(operands[0], labels, current_address)
        rd = 0 # Not used

    elif mnemonic in ["MOV", "ADD", "SUB", "CMP", "MUL", "OR", "XOR", "RET", "CALL"]:
        # Handle RET pseudo-instruction
        if mnemonic == "RET":
            if len(operands) != 0:
                raise AssemblerError(f"RET expects 0 operands, got {len(operands)}")
            # Expands to: BRANCH JREG, lr
            opcode = OPCODES["BRANCH"]
            rd = BRANCH_CONDS["JREG"]
            imm8 = REGISTERS["LR"] # Target register is lr (r14)
            return scramble_instruction(opcode, rd, imm8)

        # Handle CALL pseudo-instruction
        if mnemonic == "CALL":
            if len(operands) != 1:
                raise AssemblerError(f"CALL expects 1 operand (a label), got {len(operands)}")
            label = operands[0]
            target_addr = parse_operand(label, labels, current_address)

            words = []
            # We need to load a 16-bit address into r13.
            # Use LUI for the high byte and LDI for the low byte.
            addr_high = (target_addr >> 8) & 0xFF
            addr_low = target_addr & 0xFF

            # 1. LUI r13, <addr_high>
            if True or addr_high > 0:
                lui_word = scramble_instruction(OPCODES["LUI"], REGISTERS["R13"], addr_high)
                words.append(lui_word)

            # 2. LDI r13, <addr_low>
            # Note: LDI clears the high byte, so we must use LUI first.
            # The LUI implementation in the decoder is actually an OR, so we are good.
            ldi_word = scramble_instruction(OPCODES["LDI"], REGISTERS["R13"], addr_low)
            words.append(ldi_word)

            # 3. BRANCH CALL, r13
            branch_word = scramble_instruction(OPCODES["BRANCH"], BRANCH_CONDS["CALL"], REGISTERS["R13"])
            words.append(branch_word)
            return words


        # OP Rd, Rs
        if len(operands) != 2:
            raise AssemblerError(f"{mnemonic} expects 2 operands, got {len(operands)}")
        rd = parse_operand(operands[0], labels, current_address)
        rs = parse_operand(operands[1], labels, current_address)
        imm8 = rs # Rs is stored in the lower 4 bits of the immediate

    elif mnemonic in ["LDI", "LUI"]:
        # OP Rd, Imm8
        if len(operands) != 2:
            raise AssemblerError(f"{mnemonic} expects 2 operands, got {len(operands)}")
        rd = parse_operand(operands[0], labels, current_address)
        imm8 = parse_operand(operands[1], labels, current_address)

    elif mnemonic == "LDM":
        # LDM Rd, [Rs]
        if len(operands) != 2:
            raise AssemblerError(f"LDM expects 2 operands, got {len(operands)}")
        rd = parse_operand(operands[0], labels, current_address)
        # Allow syntax like [r1]
        rs_str = operands[1].replace('[', '').replace(']', '')
        rs = parse_operand(rs_str, labels, current_address)
        imm8 = rs

    elif mnemonic == "STM":
        # STM [Rd], Rs
        if len(operands) != 2:
            raise AssemblerError(f"STM expects 2 operands, got {len(operands)}")
        rd_str = operands[0].replace('[', '').replace(']', '')
        rd = parse_operand(rd_str, labels, current_address)
        rs = parse_operand(operands[1], labels, current_address)
        imm8 = rs

    elif mnemonic == "PUSH":
        # PUSH Rs
        if len(operands) != 1:
            raise AssemblerError(f"PUSH expects 1 operand, got {len(operands)}")
        rs = parse_operand(operands[0], labels, current_address)
        rd = 0 # Not used, but rd field is part of encoding
        imm8 = rs

    elif mnemonic == "POP":
        # POP Rd
        if len(operands) != 1:
            raise AssemblerError(f"POP expects 1 operand, got {len(operands)}")
        rd = parse_operand(operands[0], labels, current_address)
        imm8 = 0 # Not used

    elif mnemonic == "SHL":
        # SHL Rd, Imm4
        if len(operands) != 2:
            raise AssemblerError(f"SHL expects 2 operands, got {len(operands)}")
        rd = parse_operand(operands[0], labels, current_address)
        imm4 = parse_operand(operands[1], labels, current_address)
        if not (0 <= imm4 <= 0xF):
            raise AssemblerError(f"SHL immediate must be a 4-bit value (0-15), got {imm4}")
        imm8 = imm4

    elif mnemonic == "BRANCH":
        # BRANCH Cond, Target
        if len(operands) != 2:
            raise AssemblerError(f"BRANCH expects 2 operands, got {len(operands)}")
        cond_str = operands[0].upper()
        if cond_str not in BRANCH_CONDS:
            raise AssemblerError(f"Invalid branch condition: {cond_str}")
        rd = BRANCH_CONDS[cond_str] # Condition code goes in Rd field

        target = operands[1]
        # Type A: Relative Branch (Cond 0x0 - 0xD)
        if rd <= 0xD:
            target_addr = parse_operand(target, labels, current_address)
            # Relative offset = Target Address - (Current Instruction Address + 1)
            # The PC will have already been incremented by the fetcher.
            offset = target_addr - (current_address + 1)
            if not (-128 <= offset <= 127):
                raise AssemblerError(f"Branch target {target} is too far for relative jump (offset {offset}).")
            imm8 = offset & 0xFF # Store as 8-bit two's complement
        # Type B: Indirect Jump (Cond 0xE - 0xF)
        else: # CALL or JREG
            # Target is a register
            reg = parse_operand(target, labels, current_address)
            if not (0 <= reg <= 0xF):
                raise AssemblerError(f"CALL/JREG target must be a register (r0-r15), got {target}")
            imm8 = reg # Register index is stored in lower 4 bits of imm8

    return scramble_instruction(opcode, rd, imm8)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.asm> <output.bin>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r') as f:
        lines = f.readlines()

    # --- Pass 1: Find labels ---
    labels = {}
    clean_lines = []
    address = 0
    for i, line in enumerate(lines):
        line = line.split(';')[0].strip() # Remove comments and whitespace
        if not line:
            continue

        match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*):$', line)
        if match:
            label_name = match.group(1)
            if label_name in labels:
                raise AssemblerError(f"Duplicate label '{label_name}' on line {i+1}")
            labels[label_name] = address
        else:
            # Check for CALL pseudo-instruction to expand it
            parts = re.split(r'[\s,]+', line.strip(), maxsplit=1)
            mnemonic = parts[0].upper()
            if mnemonic == "CALL":
                operands_str = parts[1] if len(parts) > 1 else ""
                operands = [op.strip() for op in operands_str.split(',') if op.strip()]
                if len(operands) != 1:
                    raise AssemblerError(f"CALL expects 1 operand (a label), got {len(operands)}")
                
                # CALL can expand to 2 or 3 instructions depending on address size.
                # To keep label offsets correct, we must know the target address here.
                # This is a limitation of this simple assembler; we will assume 3 instructions
                # for address calculation purposes. A more advanced assembler would do more
                # complex passes to optimize this.
                address += 3 # Reserve space for LUI, LDI, BRANCH
            else:
                address += 1 # Each instruction is 2 bytes but 1 slot
            clean_lines.append((line, i + 1))

    # --- Pass 2: Assemble ---
    machine_code = bytearray()
    address = 0
    for line, line_num in clean_lines:
        try:
            instruction_words = assemble_line(line, labels, address)
            if isinstance(instruction_words, list):
                for word in instruction_words:
                    machine_code.extend(word.to_bytes(2, 'little'))
                address += len(instruction_words) * 1
            else: # It's a single word
                instruction_word = instruction_words
                # Append as little-endian 16-bit integer
                machine_code.extend(instruction_word.to_bytes(2, 'little'))
                address += 1
        except AssemblerError as e:
            print(f"Error on line {line_num}: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred on line {line_num}: {e}")
            sys.exit(1)

    # --- Write output ---
    with open(output_file, 'wb') as f:
        f.write(machine_code)

    print(f"Assembled {len(machine_code) // 2} instructions ({len(machine_code)} bytes).")
    print(f"Output written to {output_file}")

if __name__ == "__main__":
    main()


"""
Example Usage:

1. Save the code above as `asm.py` in the `rev/split-brain` directory.
2. Create a file `test.asm` with the following content:

; Simple program to print 'HI'

main:
    LDI  r0, 0x48   ; Load 'H' into R0
    SYS  PUTC       ; Print char in R0
    LDI  r0, 0x49   ; Load 'I' into R0
    SYS  PUTC       ; Print char in R0
    LDI  r0, 0x0A   ; Load newline
    SYS  PUTC

    BRANCH AL, end_loop ; Unconditional jump to end_loop

end_loop:
    SYS HALT

3. Run the assembler:
   python3 asm.py test.asm program.bin

4. This will create `program.bin`, which can be used with the VM.
"""