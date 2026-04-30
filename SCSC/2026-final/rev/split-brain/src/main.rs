use nix::sys::wait::{WaitStatus, waitpid};
use nix::unistd::{ForkResult, Pid, close, dup, dup2_stdin, dup2_stdout, fork, pipe, write};
use std::os::fd::{AsRawFd, OwnedFd};
use std::process::ExitCode;

#[cfg(not(feature = "embed_challenge"))]
use std::{env, fs};
use strum::{EnumCount, IntoEnumIterator};

mod error;
mod message;
mod operations;
mod units;

use error::Result;

fn setup_fds(pipe_ends: Vec<(OwnedFd, OwnedFd)>, role: units::ProcessRole) -> Result<()> {
    // Child 'i' reads from the pipe that process '(i-1+N)%N' writes to.
    let input_pipe_idx: usize =
        ((role as usize) + units::ProcessRole::COUNT - 1) % units::ProcessRole::COUNT;
    // Child 'i' writes to the pipe that process 'i' itself owns (to send to (i+1)%N).
    let output_pipe_idx: usize = role as usize;

    let read_fd_from_prev = &pipe_ends[input_pipe_idx].0.as_raw_fd(); // Read end of the pipe from previous process
    let write_fd_to_next = &pipe_ends[output_pipe_idx].1.as_raw_fd(); // Write end of the pipe to next process

    // Close all pipe ends that this child will NOT use.
    for (r, w) in pipe_ends.into_iter() {
        if r.as_raw_fd() != read_fd_from_prev.as_raw_fd() {
            close(r)?;
        } else {
            // Redirect stdin to the read end of the input pipe
            dup2_stdin(r)?;
        }
        if w.as_raw_fd() != write_fd_to_next.as_raw_fd() {
            close(w)?;
        } else {
            // Redirect stdout to the write end of the output pipe
            dup2_stdout(w)?;
        }
    }
    Ok(())
}

fn run_child(
    pipe_ends: Vec<(OwnedFd, OwnedFd)>,
    loader_read_fd: Option<OwnedFd>,
    tty_fds: Option<(OwnedFd, OwnedFd)>,
    role: units::ProcessRole,
) -> Result<()> {
    setup_fds(pipe_ends, role)?;
    units::run_unit(role, tty_fds, loader_read_fd)
}

fn run_parent(
    pipe_ends: Vec<(OwnedFd, OwnedFd)>,
    child_pids: Vec<Pid>,
    loader_write_fd: OwnedFd,
    program_data: Vec<u8>,
) -> Result<()> {
    // Parent must close all its own copies of the pipe FDs.
    for (r, w) in pipe_ends {
        close(r)?;
        close(w)?;
    }

    // Write the program to the loader pipe and close it.
    write(&loader_write_fd, &program_data)?;
    close(loader_write_fd)?;

    // Parent waits for all children to complete
    for child_pid in child_pids {
        match waitpid(child_pid, None) {
            Ok(status) => match status {
                WaitStatus::Exited(pid, status) => {
                    if status != 0 {
                        println!("Child {} exited with status {}", pid, status)
                    }
                }
                _ => println!("Unexpected status for child pid {}", child_pid),
            },
            Err(e) => eprintln!("Error waiting for child {}: {}", child_pid, e),
        }
    }
    Ok(())
}

fn run() -> Result<()> {
    
    let program_data = {
        #[cfg(not(feature = "embed_challenge"))]
        {
            let args: Vec<String> = env::args().collect();
            if args.len() != 2 {
                eprintln!("Usage: {} <program.bin>", args[0]);
                return Err(error::ProgramError::SetupError);
            }
            let program_file = &args[1];
            fs::read(program_file)?
        }

        // In release mode, embed the flag checker binary directly into the executable.
        #[cfg(feature = "embed_challenge")]
        include_bytes!("../programs/flag_checker.bin").to_vec()
    };

    // Store child PIDs for waiting later
    let mut children_pids = Vec::with_capacity(units::ProcessRole::COUNT);
    let mut pipe_ends: Vec<(OwnedFd, OwnedFd)> = Vec::with_capacity(units::ProcessRole::COUNT);

    // Create a dedicated pipe for loading the program into memory.
    let (loader_read_fd, loader_write_fd) = pipe()?;

    // Create pipes.
    for _ in 0..units::ProcessRole::COUNT {
        let (read_fd, write_fd) = pipe()?;
        pipe_ends.push((read_fd, write_fd));
    }

    // Fork child processes. The parent needs to keep all FDs open until all children
    // are forked, so they can be inherited.
    for role in units::ProcessRole::iter() {
        match unsafe { fork() }? {
            ForkResult::Parent { child, .. } => {
                // Parent process: store child PID and continue to fork next child
                children_pids.push(child);
            }
            ForkResult::Child => {
                let stdcopies = if let units::ProcessRole::System = role {
                    Some((dup(std::io::stdin())?, dup(std::io::stdin())?))
                } else {
                    None
                };

                let loader_read_fd = if let units::ProcessRole::Memory = role {
                    Some(loader_read_fd)
                } else {
                    close(loader_read_fd)?;
                    None
                };

                // Child process: close the write end of the loader pipe.
                close(loader_write_fd)?;

                return run_child(pipe_ends, loader_read_fd, stdcopies, role);
            }
        }
    }

    // Parent process: close the read end of the loader pipe as it's not needed.
    close(loader_read_fd)?;
    run_parent(pipe_ends, children_pids, loader_write_fd, program_data)
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(err) => {
            eprintln!("ERROR: {}", err);
            ExitCode::FAILURE
        }
    }
}
