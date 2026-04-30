Here is the complete specification for the **Ring-16 v5 Architecture**.

### 1. Instruction Encoding

The binary format is **nibble-scrambled**. You must unscramble the nibbles to retrieve the Logical components.

- **Physical (Binary) Layout:** `[Imm_Low: 4] [Dest: 4] [Opcode: 4] [Imm_High: 4]`
- **Logical (Decoded) Layout:** `[Opcode: 4] [Dest: 4] [Src/Imm: 8]`

**Operand Legend:**

- **Rd:** Destination Register (4 bits).
- **Rs:** Source Register (Lower 4 bits of the Src/Imm byte).
- **Imm8:** 8-bit Immediate value.
- **Imm4:** 4-bit Immediate value (Lower 4 bits of the Src/Imm byte).

---

### 2. Main Instruction Set

| Op        | Mnemonic   | Operands    | Flags | Description                                                                          |
| :-------- | :--------- | :---------- | :---- | :----------------------------------------------------------------------------------- |
| **`0x0`** | **SYS**    | `Imm8`      | -     | **System Call / NOP.** See **Table 3**.                                              |
| **`0x1`** | **MOV**    | `Rd, Rs`    | -     | **Move.** `Rd = Rs`. Copies value from Source to Dest.                               |
| **`0x2`** | **LDI**    | `Rd, Imm8`  | -     | **Load Immediate Low.** `Rd = ZeroExtend(Imm8)`. Top 8 bits cleared.                 |
| **`0x3`** | **LUI**    | `Rd, Imm8`  | -     | **Load Immediate High.** `Rd = (Rd & 0xFF) \| (Imm8 << 8)`. Bottom 8 bits preserved. |
| **`0x4`** | **LDM**    | `Rd, [Rs]`  | -     | **Load Word.** `Rd = Mem[Rs]`.                                                       |
| **`0x5`** | **STM**    | `[Rd], Rs`  | -     | **Store Word.** `Mem[Rd] = Rs`.                                                      |
| **`0x6`** | **PUSH**   | `Rs`        | -     | **Push Stack.** `SP -= 1`; `Mem[SP] = Rs`.                                           |
| **`0x7`** | **POP**    | `Rd`        | -     | **Pop Stack.** `Rd = Mem[SP]`; `SP += 1`.                                            |
| **`0x8`** | **ADD**    | `Rd, Rs`    | Z,C,O | **Add.** `Rd = Rd + Rs`.                                                             |
| **`0x9`** | **SUB**    | `Rd, Rs`    | Z,C,O | **Subtract.** `Rd = Rd - Rs`.                                                        |
| **`0xA`** | **CMP**    | `Rd, Rs`    | Z,C,O | **Compare.** `Flags = Rd - Rs`. Result discarded; flags updated.                     |
| **`0xB`** | **MUL**    | `Rd, Rs`    | Z,O   | **Multiply.** `Rd = (Rd * Rs) & 0xFFFF`. **O** set if result > 65535.                |
| **`0xC`** | **OR**     | `Rd, Rs`    | Z     | **Bitwise OR.** `Rd = Rd \| Rs`.                                                     |
| **`0xD`** | **XOR**    | `Rd, Rs`    | Z     | **Bitwise XOR.** `Rd = Rd ^ Rs`.                                                     |
| **`0xE`** | **SHL**    | `Rd, Imm4`  | Z,C   | **Shift Left.** `Rd = Rd << Imm4`.                                                   |
| **`0xF`** | **BRANCH** | _Cond, ..._ | -     | **Control Flow.** Conditional Branch or Indirect Jump. See **Table 4**.              |

---

### 3. Sub-Instruction Tables

#### Table 3: SYS Operations (Opcode 0x0)

The `Imm8` operand determines the system action.

| Imm8    | Name      | Description                                                        |
| :------ | :-------- | :----------------------------------------------------------------- |
| `0x00`  | **NOP**   | **No Operation.** Execution continues.                             |
| `0x01`  | **HALT**  | **System Halt.** Stops the VM / Exits process.                     |
| `0x02`  | **PUTC**  | **Print Char.** Output `(R0 & 0xFF)` to stdout.                    |
| `0x03`  | **GETC**  | **Read Char.** Read byte from stdin into `R0`.                     |
| _Other_ | -         | Reserved (Treat as NOP).                                           |

---

#### Table 4: BRANCH Operations (Opcode 0xF)

The behavior depends on the **Condition Code**, which is stored in the **`Rd` (Destination)** slot of the instruction.

**Type A: Relative Branch (Conditions 0x0 - 0xE)**

- **Target:** `IP = IP + SignExtend(Imm8)`
- **Logic:** Jump applies `Imm8` as a signed offset if the condition is met.

**Type B: Indirect Jump (Condition 0xF)**

- **Target:** `IP = Regs[Imm8 & 0xF]`
- **Logic:** Absolute jump to the address contained in the register specified by the lower 4 bits of `Imm8`.

| Cond (Rd) | Mnemonic    | Meaning                  | Flag Logic                                                          |
| :-------- | :---------- | :----------------------- | :------------------------------------------------------------------ |
| `0x0`     | **EQ / Z**  | Equal / Zero             | `Z == 1`                                                            |
| `0x1`     | **NE / NZ** | Not Equal / Not Zero     | `Z == 0`                                                            |
| `0x2`     | **CS / C**  | Carry Set / Unsigned >=  | `C == 1`                                                            |
| `0x3`     | **CC / NC** | Carry Clear / Unsigned < | `C == 0`                                                            |
| `0x4`     | **OS**      | Overflow Set             | `O == 1`                                                            |
| `0x5`     | **OC**      | Overflow Clear           | `O == 0`                                                            |
| `0x6`     | **GT**      | Signed Greater Than      | `Z==0` AND `O==S`                                                   |
| `0x7`     | **LE**      | Signed Less Equal        | `Z==1` OR `O!=S`                                                    |
| ...       | -           | _Reserved_               | Always False                                                        |
| `0xD`     | **AL**      | **Always**               | Always True (Unconditional Relative Jump)                           |
| **`0xE`** | **CALL**    | **Indirect Call**        | **R14 = PC then absolute Jump to address in Register `Imm8 & 0xF`** |
| **`0xF`** | **JREG**    | **Indirect Jump**        | **Absolute Jump to address in Register `Imm8 & 0xF`**               |

---

### 4. Registers & Flags

| Register     | Role               | Notes                                                        |
| :----------- | :----------------- | :----------------------------------------------------------- |
| **R0 - R13** | General Purpose    | Fully accessible.                                            |
| **R14**      | Link Register      | Conventionally used to store Return Addresses.               |
| **R15**      | Stack Pointer (SP) | Modified implicitly by `PUSH`/`POP`. Points to top of stack. |

| Flag  | Name     | Description                                                  |
| :---- | :------- | :----------------------------------------------------------- |
| **Z** | Zero     | Set if result is zero.                                       |
| **C** | Carry    | Set if unsigned arithmetic overflows or shift bits drop out. |
| **O** | Overflow | Set if signed arithmetic overflows or MUL exceeds 16 bits.   |
