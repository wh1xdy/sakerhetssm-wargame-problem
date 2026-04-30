use crate::operations::{MicroOperation, Register};
use crate::{error::Result, message::Message};

pub fn run() -> Result<()> {
    let msg = Message::new();
    msg.stdout_send()?;
    let mut halting = false;

    loop {
        let input_message = Message::stdin_read()?;
        let mut output_message = Message::new();
        let mut cursor = &input_message.micro_operations[..];

        #[cfg(feature = "debug_state")]
        {
            eprintln!("FETCHER: {:?}", input_message.micro_operations);
        }

        if input_message.micro_operations.is_empty() {
            //eprintln!("FETCHER: Create fetch");
            // FETCH => DECODE LOAD_RAM REG(PC)

            // DECODE MEM[PC]
            output_message
                .micro_operations
                .push(MicroOperation::DecodeOperation);
            output_message
                .micro_operations
                .push(MicroOperation::LoadMem);
            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(Register::PC));

            // PC = PC + 1
            output_message
                .micro_operations
                .push(MicroOperation::StoreReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(Register::PC));
            output_message
                .micro_operations
                .push(MicroOperation::Add(false));
            output_message
                .micro_operations
                .push(MicroOperation::Value(1));
            output_message
                .micro_operations
                .push(MicroOperation::LoadReg);
            output_message
                .micro_operations
                .push(MicroOperation::Register(Register::PC));
        } else {
            loop {
                match cursor {
                    [MicroOperation::Halting(count), rest @ ..] => {
                        halting = true;
                        output_message
                            .micro_operations
                            .push(MicroOperation::Halting(count - 1));

                        cursor = rest;
                    }

                    [MicroOperation::Drop, MicroOperation::Value(_), rest @ ..] => {
                        cursor = rest;
                    }

                    [head, rest @ ..] => {
                        output_message.micro_operations.push(head.clone());
                        cursor = rest;
                    }

                    [] => {
                        break;
                    }
                }
            }
        }
        //eprintln!("FETCHER: opcount {}", msg.micro_operations.len());
        output_message.stdout_send()?;
        if halting {
            return Ok(());
        }
    }
}
