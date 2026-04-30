use std::os::fd::OwnedFd;

use crate::error::{ProgramError, Result};

mod arithmetic;
mod bitwise;
mod decoder;
mod fetcher;
mod memory;
mod registers;
mod system;

#[derive(Clone, Copy, strum::FromRepr, strum::EnumIter, strum_macros::EnumCount)]
#[cfg_attr(debug_assertions, derive(Debug))]
pub enum ProcessRole {
    Fetcher,
    Decoder,
    Registers,
    Memory,
    Arithmetic,
    Bitwise,
    System,
}

pub fn run_unit(
    role: ProcessRole,
    tty_fds: Option<(OwnedFd, OwnedFd)>,
    loader_fd: Option<OwnedFd>,
) -> Result<()> {
    let result = match role {
        ProcessRole::Fetcher => fetcher::run(),
        ProcessRole::Decoder => decoder::run(),
        ProcessRole::Registers => registers::run(),
        ProcessRole::Memory => {
            let loader_fd = loader_fd.ok_or(ProgramError::SetupError)?;
            memory::run(loader_fd)
        }
        ProcessRole::Arithmetic => arithmetic::run(),
        ProcessRole::Bitwise => bitwise::run(),
        ProcessRole::System => {
            // The system unit gets the duplicated tty file descriptors.
            let (tty_in, tty_out) = tty_fds.ok_or(ProgramError::SetupError)?;
            system::run(tty_in, tty_out)
        }
    };

    #[cfg(feature = "debug_state")]
    {
        eprintln!("{:?}: EXIT", role);
    }

    result
}
