use crate::operations::MicroOperation;
use crate::{error::Result, message::Message};
use std::fs::File;
use std::io::Read;
use std::os::fd::{FromRawFd, IntoRawFd, OwnedFd};

pub fn run(loader_fd: OwnedFd) -> Result<()> {
    let mut state = [0u16; 0x10000];
    let mut halting = false;

    let mut loader_file = unsafe { File::from_raw_fd(loader_fd.into_raw_fd()) };
    let mut program_bytes = Vec::new();
    loader_file.read_to_end(&mut program_bytes)?;

    // The program is a series of little-endian u16s.
    // We load them into our u16 memory array.
    for (i, chunk) in program_bytes.chunks_exact(2).enumerate() {
        if i < state.len() {
            // chunk[0] is low byte, chunk[1] is high byte
            state[i] = u16::from_le_bytes([chunk[0], chunk[1]]);
        }
    }

    loop {
        let input_message = Message::stdin_read()?;
        let mut output_message = Message::new();
        let mut cursor = &input_message.micro_operations[..];

        #[cfg(feature = "debug_state")]
        {
            eprintln!("MEMORY: {:?}", input_message.micro_operations);
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
                    MicroOperation::LoadMem,
                    MicroOperation::Value(value),
                    rest @ ..,
                ] => {
                    let mem_value = state[*value as usize];
                    output_message
                        .micro_operations
                        .push(MicroOperation::Value(mem_value));

                    cursor = rest;
                }

                [
                    MicroOperation::StoreMem,
                    MicroOperation::Value(address),
                    MicroOperation::Value(value),
                    rest @ ..,
                ] => {
                    state[*address as usize] = *value;
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
