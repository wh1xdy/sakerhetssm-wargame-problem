use fixed_map::Map;

use crate::operations::{
    BranchCondition, FLAG_C_MASK, FLAG_O_MASK, FLAG_Z_MASK, Flag, MicroOperation, Register, Value,
};
use crate::{error::Result, message::Message};

pub fn run() -> Result<()> {
    let mut state: Map<Register, Value> = Map::new();
    let mut halting = false;
    loop {
        let input_message = Message::stdin_read()?;
        let mut output_message = Message::new();
        let mut cursor = &input_message.micro_operations[..];

        #[cfg(feature = "debug_state")]
        {
            eprintln!("REGISTERS: {:?}", input_message.micro_operations);
        }

        loop {
            match cursor {
                [MicroOperation::Halting(count), rest @ ..] => {
                    halting = true;
                    output_message
                        .micro_operations
                        .push(MicroOperation::Halting(count - 1));

                    cursor = rest;
                }

                [
                    MicroOperation::LoadReg,
                    MicroOperation::Register(reg),
                    rest @ ..,
                ] => {
                    let reg_value = state.get(*reg).unwrap_or(&0);
                    output_message
                        .micro_operations
                        .push(MicroOperation::Value(*reg_value));

                    cursor = rest;
                }

                [
                    MicroOperation::StoreReg,
                    MicroOperation::Register(reg),
                    MicroOperation::Value(value),
                    rest @ ..,
                ] => {
                    state.insert(*reg, *value);
                    cursor = rest;
                }

                [MicroOperation::SetFlag(flag), rest @ ..] => {
                    let mut flags = state.get(Register::Flags).unwrap_or(&0).to_owned();
                    let mask = match flag {
                        Flag::Zero => FLAG_Z_MASK,
                        Flag::Carry => FLAG_C_MASK,
                        Flag::Overflow => FLAG_O_MASK,
                    };
                    flags |= mask;
                    state.insert(Register::Flags, flags);
                    cursor = rest;
                }
                [MicroOperation::ClearFlag(flag), rest @ ..] => {
                    let mut flags = state.get(Register::Flags).unwrap_or(&0).to_owned();
                    let mask = match flag {
                        Flag::Zero => FLAG_Z_MASK,
                        Flag::Carry => FLAG_C_MASK,
                        Flag::Overflow => FLAG_O_MASK,
                    };
                    flags &= !mask;
                    state.insert(Register::Flags, flags);
                    cursor = rest;
                }

                [MicroOperation::Branch, MicroOperation::Value(destination)] => {
                    // Note: no  rest @ .. here because we can only branch when pipeline is clear
                    state.insert(Register::PC, *destination);
                    break;
                }

                [MicroOperation::BranchIf(cond, offset)] => {
                    // Note: no  rest @ .. here because we can only branch when pipeline is clear
                    //eprintln!("BRANCH!");
                    let flags = state.get(Register::Flags).unwrap_or(&0);
                    let z = (flags & FLAG_Z_MASK) != 0;
                    let c = (flags & FLAG_C_MASK) != 0;
                    let o = (flags & FLAG_O_MASK) != 0;

                    // The 'S' or Sign flag is implicitly the MSB of the *result* of the last
                    // operation. Since we don't track that, we can't implement GT/LE perfectly.
                    // The spec says to treat reserved/unsupported conditions as false.
                    let condition_met = match cond {
                        BranchCondition::EQ => z,
                        BranchCondition::NE => !z,
                        BranchCondition::CS => c,
                        BranchCondition::CC => !c,
                        BranchCondition::OS => o,
                        BranchCondition::OC => !o,
                        BranchCondition::AL => true,
                        // Per spec, treat unsupported conditions as false.
                        // A full implementation would require a Sign flag.
                        BranchCondition::GT | BranchCondition::LE => false,
                    };

                    if condition_met {
                        let pc = state.get(Register::PC).unwrap_or(&0);
                        // The offset is relative to the *next* instruction's address.
                        // The fetcher has already incremented PC by 2 before this instruction
                        // was even decoded. So we apply the offset to the current PC.
                        // The spec says `IP = IP + SignExtend(Imm8)`, but our PC is already IP+2.
                        // So we do `PC = (PC-2) + offset + 2`, which simplifies to `PC = PC + offset`.
                        let new_pc = pc.wrapping_add_signed(*offset as i16);
                        state.insert(Register::PC, new_pc);
                    }
                    //cursor = rest;
                    break;
                }
                [head, rest @ ..] => {
                    output_message.micro_operations.push(head.clone());
                    cursor = rest;
                }

                // End of stream
                [] => break,
            }
        }

        output_message.stdout_send()?;
        if halting {
            return Ok(());
        }
    }
}
