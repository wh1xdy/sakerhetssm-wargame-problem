use crate::error::ProgramError;
use crate::operations::{BranchCondition, MicroOperation, Register};
use crate::{error::Result, message::Message};

pub fn run() -> Result<()> {
    let mut halting = false;
    loop {
        let input_message = Message::stdin_read()?;
        //eprintln!("DECODER: opcount {}", msg.micro_operations.len());

        #[cfg(feature = "debug_state")]
        {
            eprintln!("DECODER: {:?}", input_message.micro_operations);
        }

        let output_message = process_decoder(input_message, &mut halting)?;
        output_message.stdout_send()?;
        if halting {
            return Ok(());
        }
    }
}

fn process_decoder(input_message: Message, halting: &mut bool) -> Result<Message> {
    let mut output_message = Message::new();
    let mut cursor = &input_message.micro_operations[..];

    loop {
        match cursor {
            [MicroOperation::Halting(count), rest @ ..] => {
                *halting = true;
                output_message
                    .micro_operations
                    .push(MicroOperation::Halting(count - 1));

                cursor = rest;
            }

            [
                MicroOperation::DecodeOperation,
                MicroOperation::Value(instruction),
                rest @ ..,
            ] => {
                decode_instruction(&mut output_message, instruction)?;

                cursor = rest;
            }

            [head, rest @ ..] => {
                output_message.micro_operations.push(head.clone());
                cursor = rest;
            }

            // End of stream
            [] => break,
        }
    }

    Ok(output_message)
}

pub struct Instruction {
    pub opcode: u8, // 4 bits
    pub rd: u8,     // 4 bits (Destination Register or Condition Code)
    pub rs: u8,     // 4 bits (Source Register)
    pub imm8: u8,   // 8 bits (Full Immediate)
    pub imm4: u8,   // 4 bits (Lower nibble of Immediate / Shift Amount)
}

impl Instruction {
    /// Decodes a scrambled Ring-16 instruction word.
    /// Physical Layout: [Imm_Low: 4] [Dest: 4] [Opcode: 4] [Imm_High: 4]
    ///                   (15..12)     (11..8)    (7..4)       (3..0)
    pub fn decode(raw: &u16) -> Self {
        // Extract nibbles using bitmasks and shifts
        let imm_low = (raw & 0xF000) >> 12;
        let rd = (raw & 0x0F00) >> 8;
        let opcode = (raw & 0x00F0) >> 4;
        let imm_high = raw & 0x000F;

        // Reconstruct the Logical Immediate (Imm8)
        // Logical: [Imm_High] [Imm_Low]
        let imm8 = ((imm_high as u8) << 4) | (imm_low as u8);

        Self {
            opcode: opcode as u8,
            rd: rd as u8,

            // For Register-Register ops (ADD Rd, Rs), Rs is the lower nibble
            rs: imm8 & 0x0F,

            imm8,

            // Alias for clarity (used in Shifts)
            imm4: imm8 & 0x0F,
        }
    }
}

fn decode_instruction(output_message: &mut Message, instruction: &u16) -> Result<()> {
    let ins = Instruction::decode(instruction);

    match ins.opcode {
        // SYS
        0 => {
            let sub_op = ins.imm8;
            match sub_op {
                // NOP
                0x00 => { /* No-op, do nothing */ }
                // HALT
                0x01 => {
                    output_message.micro_operations.push(MicroOperation::Halt);
                }
                // PUTC
                0x02 => {
                    output_message.micro_operations.push(MicroOperation::PutC);
                    output_message
                        .micro_operations
                        .push(MicroOperation::LoadReg);
                    output_message
                        .micro_operations
                        .push(MicroOperation::Register(Register::R0));
                }
                // GETC
                0x03 => {
                    output_message.micro_operations.push(MicroOperation::GetC);
                }
                // Reserved, treat as NOP
                _ => {}
            }
        }
        // MOV Rd, Rs
        1 => {
            let dst_reg = Register::from_repr(ins.rd).ok_or(ProgramError::BadInstruction)?;
            let src_reg = Register::from_repr(ins.rs).ok_or(ProgramError::BadInstruction)?;

            output_message
                .micro_operations
                .push(MicroOperation::StoreReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));
            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(src_reg));
        }
        // LDI Rd, Imm8
        2 => {
            let dst_reg = Register::from_repr(ins.rd).ok_or(ProgramError::BadInstruction)?;
            let value = ins.imm8 as u16;

            output_message
                .micro_operations
                .push(MicroOperation::StoreReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));
            output_message
                .micro_operations
                .push(MicroOperation::Value(value));
        }
        // LUI Rd, Imm8
        3 => {
            let dst_reg = Register::from_repr(ins.rd).ok_or(ProgramError::BadInstruction)?;
            let value = ins.imm8 as u16;

            output_message
                .micro_operations
                .push(MicroOperation::StoreReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));
            output_message.micro_operations.push(MicroOperation::Or);
            output_message.micro_operations.push(MicroOperation::And);
            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));
            output_message
                .micro_operations
                .push(MicroOperation::Value(0xFF));
            output_message.micro_operations.push(MicroOperation::Shl);
            output_message
                .micro_operations
                .push(MicroOperation::Value(value));
            output_message
                .micro_operations
                .push(MicroOperation::Value(8));
        }
        // LDM Rd, [Rs]
        4 => {
            let dst_reg = Register::from_repr(ins.rd).ok_or(ProgramError::BadInstruction)?;
            let src_reg = Register::from_repr(ins.rs).ok_or(ProgramError::BadInstruction)?;

            output_message
                .micro_operations
                .push(MicroOperation::StoreReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));
            output_message
                .micro_operations
                .push(MicroOperation::LoadMem);
            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(src_reg));
        }
        // STM [Rd], Rs
        5 => {
            let dst_reg = Register::from_repr(ins.rd).ok_or(ProgramError::BadInstruction)?;
            let src_reg = Register::from_repr(ins.rs).ok_or(ProgramError::BadInstruction)?;

            output_message
                .micro_operations
                .push(MicroOperation::StoreMem);
            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));
            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(src_reg));
        }
        // PUSH Rs
        6 => {
            let src_reg = Register::from_repr(ins.rs).ok_or(ProgramError::BadInstruction)?;

            // 1. Decrement SP: SP = SP - 1
            output_message
                .micro_operations
                .push(MicroOperation::StoreReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(Register::SP));
            output_message.micro_operations.push(MicroOperation::Sub);
            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(Register::SP));
            output_message
                .micro_operations
                .push(MicroOperation::Value(1));

            // 2. Store Rs at new SP: Mem[SP-1] = Rs
            // We must re-calculate SP-1 because the updated SP is not available in this cycle.
            output_message
                .micro_operations
                .push(MicroOperation::StoreMem);
            output_message.micro_operations.push(MicroOperation::Sub);
            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(Register::SP));
            output_message
                .micro_operations
                .push(MicroOperation::Value(1));
            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(src_reg));
        }
        // POP Rd
        7 => {
            let dst_reg = Register::from_repr(ins.rd).ok_or(ProgramError::BadInstruction)?;

            // 1. Load value from SP: Rd = Mem[SP]
            output_message
                .micro_operations
                .push(MicroOperation::StoreReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));
            output_message
                .micro_operations
                .push(MicroOperation::LoadMem);
            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(Register::SP));

            // 2. Increment SP: SP = SP + 1
            output_message
                .micro_operations
                .push(MicroOperation::StoreReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(Register::SP));
            output_message
                .micro_operations
                .push(MicroOperation::Add(false));
            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(Register::SP));
            output_message
                .micro_operations
                .push(MicroOperation::Value(1));
        }
        // ADD Rd, Rs
        8 => {
            let dst_reg = Register::from_repr(ins.rd).ok_or(ProgramError::BadInstruction)?;
            let src_reg = Register::from_repr(ins.rs).ok_or(ProgramError::BadInstruction)?;

            output_message
                .micro_operations
                .push(MicroOperation::StoreReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));
            output_message
                .micro_operations
                .push(MicroOperation::Add(true));

            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));

            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(src_reg));
        }
        // SUB Rd, Rs
        9 => {
            let dst_reg = Register::from_repr(ins.rd).ok_or(ProgramError::BadInstruction)?;
            let src_reg = Register::from_repr(ins.rs).ok_or(ProgramError::BadInstruction)?;

            output_message
                .micro_operations
                .push(MicroOperation::StoreReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));
            output_message.micro_operations.push(MicroOperation::Sub);

            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));

            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(src_reg));
        }
        // CMP Rd, Rs
        10 => {
            let dst_reg = Register::from_repr(ins.rd).ok_or(ProgramError::BadInstruction)?;
            let src_reg = Register::from_repr(ins.rs).ok_or(ProgramError::BadInstruction)?;

            output_message.micro_operations.push(MicroOperation::Drop);
            output_message.micro_operations.push(MicroOperation::Sub);

            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));

            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(src_reg));
        }
        // MUL Rd, Rs
        11 => {
            let dst_reg = Register::from_repr(ins.rd).ok_or(ProgramError::BadInstruction)?;
            let src_reg = Register::from_repr(ins.rs).ok_or(ProgramError::BadInstruction)?;

            output_message
                .micro_operations
                .push(MicroOperation::StoreReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));
            output_message.micro_operations.push(MicroOperation::Mul);

            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));

            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(src_reg));
        }
        12 => {
            let dst_reg = Register::from_repr(ins.rd).ok_or(ProgramError::BadInstruction)?;
            let src_reg = Register::from_repr(ins.rs).ok_or(ProgramError::BadInstruction)?;

            output_message
                .micro_operations
                .push(MicroOperation::StoreReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));
            output_message.micro_operations.push(MicroOperation::Or);

            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));

            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(src_reg));
        }
        13 => {
            let dst_reg = Register::from_repr(ins.rd).ok_or(ProgramError::BadInstruction)?;
            let src_reg = Register::from_repr(ins.rs).ok_or(ProgramError::BadInstruction)?;

            output_message
                .micro_operations
                .push(MicroOperation::StoreReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));
            output_message.micro_operations.push(MicroOperation::Xor);

            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));

            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(src_reg));
        }
        14 => {
            let dst_reg = Register::from_repr(ins.rd).ok_or(ProgramError::BadInstruction)?;
            let shift_amount = ins.imm4 as u16;

            output_message
                .micro_operations
                .push(MicroOperation::StoreReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));
            output_message.micro_operations.push(MicroOperation::Shl);

            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(dst_reg));

            output_message
                .micro_operations
                .push(MicroOperation::Value(shift_amount));
        }
        15 => {
            let condition_code = ins.rd;
            match condition_code {
                // Type A: Relative Branch
                0..=0x7 | 0xD => {
                    let condition = match condition_code {
                        0x0 => BranchCondition::EQ,
                        0x1 => BranchCondition::NE,
                        0x2 => BranchCondition::CS,
                        0x3 => BranchCondition::CC,
                        0x4 => BranchCondition::OS,
                        0x5 => BranchCondition::OC,
                        0x6 => BranchCondition::GT,
                        0x7 => BranchCondition::LE,
                        0xD => BranchCondition::AL,
                        _ => return Err(ProgramError::BadInstruction), // Should be unreachable
                    };
                    let offset = ins.imm8 as i8;
                    output_message
                        .micro_operations
                        .push(MicroOperation::BranchIf(condition, offset));
                }
                // Type B: Indirect Jump/Call
                0xE | 0xF => {
                    // The target register is in the lower 4 bits of imm8
                    let target_reg =
                        Register::from_repr(ins.imm4).ok_or(ProgramError::BadInstruction)?;

                    // For CALL, first store the current PC into the Link Register (R14)
                    if condition_code == 0xe {
                        output_message
                            .micro_operations
                            .push(MicroOperation::StoreReg);
                        output_message
                            .micro_operations
                            .push(MicroOperation::Register(Register::R14));

                        output_message
                            .micro_operations
                            .push(MicroOperation::Add(false));
                        output_message
                            .micro_operations
                            .push(MicroOperation::LoadReg);

                        output_message
                            .micro_operations
                            .push(MicroOperation::Register(Register::PC));
                        output_message
                            .micro_operations
                            .push(MicroOperation::Value(1));
                    }

                    // Create a branch micro op which will execute once pipeline is clear
                    output_message.micro_operations.push(MicroOperation::Branch);
                    output_message
                        .micro_operations
                        .push(MicroOperation::LoadReg);
                    output_message
                        .micro_operations
                        .push(MicroOperation::Register(target_reg));
                }
                _ => return Err(crate::error::ProgramError::BadInstruction),
            }
        }
        _ => return Err(crate::error::ProgramError::BadInstruction),
    }

    Ok(())
}
