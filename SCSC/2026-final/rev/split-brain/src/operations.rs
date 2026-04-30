use serde::{Deserialize, Serialize};

#[derive(Clone, Copy, Serialize, Deserialize, fixed_map::Key, strum::FromRepr)]
#[repr(u8)]
#[cfg_attr(debug_assertions, derive(Debug))]
pub enum Register {
    R0,
    R1,
    R2,
    R3,
    R4,
    R5,
    R6,
    R7,
    R8,
    R9,
    R10,
    R11,
    R12,
    R13,
    R14,
    SP,
    PC,
    Flags,
}

pub type Value = u16;

#[derive(Clone, Copy, Serialize, Deserialize)]
#[cfg_attr(debug_assertions, derive(Debug))]
pub enum Flag {
    Zero,     // Z
    Carry,    // C
    Overflow, // O
}

pub const FLAG_Z_MASK: u16 = 1 << 0;
pub const FLAG_C_MASK: u16 = 1 << 1;
pub const FLAG_O_MASK: u16 = 1 << 2;

#[derive(Clone, Copy, Serialize, Deserialize)]
#[cfg_attr(debug_assertions, derive(Debug))]
pub enum BranchCondition {
    EQ, // Z == 1
    NE, // Z == 0
    CS, // C == 1
    CC, // C == 0
    OS, // O == 1
    OC, // O == 0
    GT, // Signed Greater Than
    LE, // Signed Less or Equal
    AL, // Always
}

/*
add A, B =>
    STORE REG(A) ADD REG_LOAD REG(A) REG_LOAD REG(B)
    STORE REG(A) ADD VALUE(X) VALUE(Y)
    STORE REG(A) VALUE(Y)


*/

#[derive(Clone, Serialize, Deserialize)]
#[repr(u8)]
#[cfg_attr(debug_assertions, derive(Debug))]
pub enum MicroOperation {
    FetchOperation,
    DecodeOperation,
    Value(Value),
    Register(Register),
    LoadReg,
    StoreReg,
    LoadMem,
    StoreMem,
    Drop,

    Add(bool),
    Sub,
    Mul,
    Div,

    Shl,
    Shr,

    And,
    Or,
    Xor,
    Not,

    Halting(usize),
    Halt,
    GetC,
    PutC,

    SetFlag(Flag),
    ClearFlag(Flag),

    BranchIf(BranchCondition, i8),
    Branch,
}
