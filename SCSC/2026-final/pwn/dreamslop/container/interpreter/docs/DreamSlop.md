# DreamSlop

DreamSlop is a small dialect of [Dreamberd](https://github.com/TodePond/DreamBerd): same spirit, shipped as a C tree-walking interpreter with a REPL and a `.db` file runner.

## Slop heap (memory model)

DreamSlop uses a **Slop heap**: every page that holds interpreter-allocated data is mapped **read–write–execute**. The language spec treats this as a feature so your programs can be *maximally expressive* (do not run untrusted DreamSlop on machines you care about).

Implementation detail: when a freed block is eligible for reuse, the **next** allocation of the **same size** may be satisfied from that block (documented allocator behavior).

## Building

```bash
make
```

Produces `./dreamslop`. Requires a C11 compiler and libm.

```bash
./dreamslop                 # REPL
./dreamslop program.db      # run a file
```

## REPL

End statements with `!` or `?`. Multi-line input continues until a terminator appears.

```
DreamSlop REPL -- end statements with '!' (or '?').  Ctrl-D to exit.
db>  const const x = 1!
```

See `examples/*.db` in this directory for runnable samples.
