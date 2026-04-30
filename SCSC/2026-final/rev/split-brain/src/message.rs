use std::io::{stdin, stdout};

use crate::{error::ProgramError, operations::MicroOperation};
use postcard::{from_io, to_io};
use serde::{Deserialize, Serialize};
use std::io::Write;

#[derive(Serialize, Deserialize)]
#[cfg_attr(debug_assertions, derive(Debug))]
pub struct Message {
    pub micro_operations: Vec<MicroOperation>,
}

impl Message {
    pub fn new() -> Self {
        Self {
            micro_operations: Vec::new(),
        }
    }

    pub fn stdin_read() -> Result<Self, ProgramError> {
        let stdin = stdin();
        let stdin = stdin.lock();

        let mut buf = [0; 1024];
        let (message, _) = from_io((stdin, &mut buf))?;

        Ok(message)
    }

    pub fn stdout_send(&self) -> Result<(), ProgramError> {
        let stdout = stdout();
        let mut stdout = stdout.lock();

        to_io(self, &mut stdout)?;
        stdout.flush()?;

        Ok(())
    }
}
