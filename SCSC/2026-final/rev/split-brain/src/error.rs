use thiserror::Error;

#[derive(Error, Debug)]
pub enum ProgramError {
    #[error("unix error: {0}")]
    Unix(#[from] nix::Error),

    #[error("IO error: {0}")]
    IO(#[from] std::io::Error),

    #[error("Postcard error: {0}")]
    Postcard(#[from] postcard::Error),

    #[error("Bad instruction")]
    BadInstruction,

    #[error("Setup error")]
    SetupError,
}

pub type Result<T> = std::result::Result<T, ProgramError>;
