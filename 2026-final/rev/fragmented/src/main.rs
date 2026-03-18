use hex_literal::hex;
use rayon::prelude::*;
use std::convert::TryFrom;
use std::io::BufRead;
use std::num::TryFromIntError;
use thiserror::Error;
use wasmtime::*;

// ./generator 'SSM{eXcit1nG_0x1de_and_WASMT1M3}'
const TARGET: [u8; 32] = hex!("b85ac087d696ecf7e9fcd98b757e775fd94850096642d0c9865ac04a9357bcbb");

#[derive(Error, Debug)]
pub enum Error {
    #[error("Wasmtime: {0}")]
    Wasmtime(#[from] wasmtime::Error),

    #[error("integer: {0}")]
    Integer(#[from] TryFromIntError),
}

fn main() -> Result<(), Error> {
    let engine = Engine::default();

    let module_code = [
        include_bytes!("../modules/module1.cwasm"),
        include_bytes!("../modules/module2.cwasm"),
        include_bytes!("../modules/module3.cwasm"),
        include_bytes!("../modules/module4.cwasm"),
        include_bytes!("../modules/module5.cwasm"),
        include_bytes!("../modules/module6.cwasm"),
        include_bytes!("../modules/module7.cwasm"),
        include_bytes!("../modules/module8.cwasm"),
    ];

    let modules: Result<Vec<Module>, _> = module_code
        .into_iter()
        .map(|module| unsafe { Module::deserialize(&engine, module) })
        .collect();
    let modules = match modules {
        Ok(modules) => modules,
        Err(error) => {
            println!("failed to deserialize pre-compiled module: {error:?}");
            return Ok(());
        }
    };

    let linker = Linker::new(&engine);

    print!("Flag: ");
    let stdin = std::io::stdin();
    let input = stdin.lock().lines().next().unwrap().unwrap();

    let result: Result<Vec<u8>, Error> = input
        .as_bytes()
        .par_iter()
        .enumerate()
        .map(|(index, b)| -> Result<u8, Error> {
            let mut store = Store::new(&engine, ());
            let module_index = index % modules.len();
            let module = &modules[module_index];
            let instance = linker.instantiate(&mut store, module)?;
            let function = instance
                .get_typed_func::<i32, i32>(&mut store, &format!("process{}", module_index + 1))?;
            let output = function.call(&mut store, (*b).into())?;
            Ok(u8::try_from(output)?)
        })
        .collect();

    let result = match result {
        Ok(result) => result,
        Err(error) => {
            println!("failed to validate flag: {error:?}");
            return Ok(());
        }
    };

    if result == TARGET {
        println!("Correct!");
    } else {
        println!("Incorrect.");
    }

    Ok(())
}
