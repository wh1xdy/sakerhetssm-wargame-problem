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
            eprintln!("BITWISE {:?}", input_message.micro_operations);
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
                    MicroOperation::And,
                    MicroOperation::Value(left),
                    MicroOperation::Value(right),
                    rest @ ..,
                ] => {
                    let result = left & right;
                    if result == 0 {
                        output_message
                            .micro_operations
                            .push(MicroOperation::SetFlag(Flag::Zero));
                    } else {
                        output_message
                            .micro_operations
                            .push(MicroOperation::ClearFlag(Flag::Zero));
                    }
                    output_message
                        .micro_operations
                        .push(MicroOperation::Value(result));
                    cursor = rest;
                }

                [
                    MicroOperation::Or,
                    MicroOperation::Value(left),
                    MicroOperation::Value(right),
                    rest @ ..,
                ] => {
                    let result = left | right;
                    if result == 0 {
                        output_message
                            .micro_operations
                            .push(MicroOperation::SetFlag(Flag::Zero));
                    } else {
                        output_message
                            .micro_operations
                            .push(MicroOperation::ClearFlag(Flag::Zero));
                    }
                    output_message
                        .micro_operations
                        .push(MicroOperation::Value(result));
                    cursor = rest;
                }

                [
                    MicroOperation::Xor,
                    MicroOperation::Value(left),
                    MicroOperation::Value(right),
                    rest @ ..,
                ] => {
                    let result = left ^ right;
                    if result == 0 {
                        output_message
                            .micro_operations
                            .push(MicroOperation::SetFlag(Flag::Zero));
                    } else {
                        output_message
                            .micro_operations
                            .push(MicroOperation::ClearFlag(Flag::Zero));
                    }
                    output_message
                        .micro_operations
                        .push(MicroOperation::Value(result));
                    cursor = rest;
                }

                [
                    MicroOperation::Shl,
                    MicroOperation::Value(left),
                    MicroOperation::Value(right),
                    rest @ ..,
                ] => {
                    let shift = right;
                    let (result, carry) = if *shift == 0 {
                        (*left, false)
                    } else if *shift >= 16 {
                        (0, (*left >> (16 - (*shift - 16))) & 1 == 1)
                    } else {
                        (*left << shift, (*left >> (16 - shift)) & 1 == 1)
                    };

                    if result == 0 {
                        output_message
                            .micro_operations
                            .push(MicroOperation::SetFlag(Flag::Zero));
                    } else {
                        output_message
                            .micro_operations
                            .push(MicroOperation::ClearFlag(Flag::Zero));
                    }
                    if carry {
                        output_message
                            .micro_operations
                            .push(MicroOperation::SetFlag(Flag::Carry));
                    } else {
                        output_message
                            .micro_operations
                            .push(MicroOperation::ClearFlag(Flag::Carry));
                    }

                    output_message
                        .micro_operations
                        .push(MicroOperation::Value(result));
                    cursor = rest;
                }

                [
                    MicroOperation::Shr,
                    MicroOperation::Value(left),
                    MicroOperation::Value(right),
                    rest @ ..,
                ] => {
                    let result = left >> right;
                    output_message
                        .micro_operations
                        .push(MicroOperation::Value(result));

                    cursor = rest;
                }

                [MicroOperation::Not, MicroOperation::Value(value), rest @ ..] => {
                    let result = !(*value);
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
