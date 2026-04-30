use strum::EnumCount;

use crate::error::Result;
use crate::message::Message;
use crate::operations::{MicroOperation, Register};
use crate::units::ProcessRole;
use std::fs::File;
use std::io::{Read, Write};
use std::os::fd::{FromRawFd, IntoRawFd, OwnedFd};

pub fn run(stdin: OwnedFd, stdout: OwnedFd) -> Result<()> {
    // Convert the OwnedFds into `File` objects, which implement Read and Write.
    // This is `unsafe` because the caller must guarantee the FDs are valid.
    let mut tty_in = unsafe { File::from_raw_fd(stdin.into_raw_fd()) };
    let mut tty_out = unsafe { File::from_raw_fd(stdout.into_raw_fd()) };
    loop {
        let input_message = Message::stdin_read()?;
        let mut output_message = Message::new();
        let mut cursor = &input_message.micro_operations[..];

        #[cfg(feature = "debug_state")]
        {
            eprintln!("SYSTEM: {:?}", input_message.micro_operations);
        }

        loop {
            match cursor {
                [MicroOperation::Halt, rest @ ..] => {
                    // Halt the entire VM by exiting this process.
                    // The parent process will detect this and shut down the others.
                    output_message
                        .micro_operations
                        .push(MicroOperation::Halting(ProcessRole::COUNT - 1));
                    cursor = rest;
                }
                [MicroOperation::Halting(0), ..] => {
                    // Halt the entire VM by exiting this process.
                    // The parent process will detect this and shut down the others.
                    return Ok(());
                }
                [MicroOperation::PutC, MicroOperation::Value(val), rest @ ..] => {
                    // The decoder requested R0, the register unit provided it. Now we print.
                    write!(tty_out, "{}", (*val & 0xFF) as u8 as char)?;
                    tty_out.flush()?;
                    // This operation is consumed and not passed on.
                    cursor = rest;
                }
                [MicroOperation::GetC, rest @ ..] => {
                    // Read a single byte from actual stdin
                    let mut buf = [0u8; 1];
                    //eprintln!("READ_1");
                    let bytes_read = tty_in.read(&mut buf)?;
                    //eprintln!("READ_2");
                    let value = if bytes_read > 0 { buf[0] as u16 } else { 0 };

                    // Create micro-ops to store the read value into R0
                    output_message
                        .micro_operations
                        .push(MicroOperation::StoreReg);
                    output_message
                        .micro_operations
                        .push(MicroOperation::Register(Register::R0));
                    output_message
                        .micro_operations
                        .push(MicroOperation::Value(value));
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
    }
}
