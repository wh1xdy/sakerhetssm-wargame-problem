use crate::operations::{Flag, MicroOperation};
use crate::{error::Result, message::Message};

pub fn run() -> Result<()> {
    loop {
        let input_message = Message::stdin_read()?;
        let mut output_message = Message::new();
        let mut cursor = &input_message.micro_operations[..];
        let mut halting = false;

        #[cfg(feature = "debug_state")]
        {
            eprintln!("ARITHMETIC: {:?}", input_message.micro_operations);
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
                    MicroOperation::Add(update_flags),
                    MicroOperation::Value(left),
                    MicroOperation::Value(right),
                    rest @ ..,
                ] => {
                    let (result, carry) = left.overflowing_add(*right);
                    let overflow =
                        (left & 0x8000) == (right & 0x8000) && (left & 0x8000) != (result & 0x8000);

                    if *update_flags {
                        // Set Z flag
                        if result == 0 {
                            output_message
                                .micro_operations
                                .push(MicroOperation::SetFlag(Flag::Zero));
                        } else {
                            output_message
                                .micro_operations
                                .push(MicroOperation::ClearFlag(Flag::Zero));
                        }
                        // Set C flag
                        if carry {
                            output_message
                                .micro_operations
                                .push(MicroOperation::SetFlag(Flag::Carry));
                        } else {
                            output_message
                                .micro_operations
                                .push(MicroOperation::ClearFlag(Flag::Carry));
                        }
                        // Set O flag
                        if overflow {
                            output_message
                                .micro_operations
                                .push(MicroOperation::SetFlag(Flag::Overflow));
                        } else {
                            output_message
                                .micro_operations
                                .push(MicroOperation::ClearFlag(Flag::Overflow));
                        }
                    }

                    output_message
                        .micro_operations
                        .push(MicroOperation::Value(result));
                    cursor = rest;
                }

                [
                    MicroOperation::Sub,
                    MicroOperation::Value(left),
                    MicroOperation::Value(right),
                    rest @ ..,
                ] => {
                    let (result, borrow) = left.overflowing_sub(*right);
                    let overflow =
                        (left & 0x8000) != (right & 0x8000) && (left & 0x8000) != (result & 0x8000);

                    // Set Z flag
                    if result == 0 {
                        output_message
                            .micro_operations
                            .push(MicroOperation::SetFlag(Flag::Zero));
                    } else {
                        output_message
                            .micro_operations
                            .push(MicroOperation::ClearFlag(Flag::Zero));
                    }
                    // Set C flag (borrow is carry for subtraction)
                    if borrow {
                        output_message
                            .micro_operations
                            .push(MicroOperation::SetFlag(Flag::Carry));
                    } else {
                        output_message
                            .micro_operations
                            .push(MicroOperation::ClearFlag(Flag::Carry));
                    }
                    // Set O flag
                    if overflow {
                        output_message
                            .micro_operations
                            .push(MicroOperation::SetFlag(Flag::Overflow));
                    } else {
                        output_message
                            .micro_operations
                            .push(MicroOperation::ClearFlag(Flag::Overflow));
                    }

                    output_message
                        .micro_operations
                        .push(MicroOperation::Value(result));
                    cursor = rest;
                }

                [
                    MicroOperation::Mul,
                    MicroOperation::Value(left),
                    MicroOperation::Value(right),
                    rest @ ..,
                ] => {
                    let full_result = (*left as u32) * (*right as u32);
                    let result = full_result as u16;
                    let overflow = full_result > 0xFFFF;

                    // Set Z flag
                    if result == 0 {
                        output_message
                            .micro_operations
                            .push(MicroOperation::SetFlag(Flag::Zero));
                    } else {
                        output_message
                            .micro_operations
                            .push(MicroOperation::ClearFlag(Flag::Zero));
                    }
                    // Set O flag
                    if overflow {
                        output_message
                            .micro_operations
                            .push(MicroOperation::SetFlag(Flag::Overflow));
                    } else {
                        output_message
                            .micro_operations
                            .push(MicroOperation::ClearFlag(Flag::Overflow));
                    }

                    output_message
                        .micro_operations
                        .push(MicroOperation::Value(result));
                    cursor = rest;
                }

                [
                    MicroOperation::Div,
                    MicroOperation::Value(left),
                    MicroOperation::Value(right),
                    rest @ ..,
                ] => {
                    let result = left / right;
                    output_message
                        .micro_operations
                        .push(MicroOperation::Value(result));

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

        output_message.stdout_send()?;
        if halting {
            return Ok(());
        }
    }
}
