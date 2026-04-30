# DreamSlop interpreter (handout)

This directory is the **player handout**: full source for the DreamSlop interpreter.

- Language notes and the **Slop heap** model: [docs/DreamSlop.md](docs/DreamSlop.md)
- Feature list and examples: see [docs/DreamSlop.md](docs/DreamSlop.md) and the `examples/` folder.

Build with `make`, run `./dreamslop` for the REPL.

## Language subset (summary)

- Statements end with `!` (or `?` for debug-style printing).
- Declarations: `const const`, `const var`, `var const`, `var var`.
- Values: numbers, strings, booleans (`true` / `false` / `maybe`), arrays, objects, functions, classes, instances, `undefined`.
- Strings support multi-quote openers and `${...}` interpolation.
- Arrays index from `-1`; `delete` removes variables, literals, types, and object keys.
- Control flow: `if` / `while` / `return`, reactive `when`, `previous` / `next`.
- Builtins: `print`, `input`, `typeof`, `len`, `String`, `Number`, `push`, `pop`, `floor`.

Details and the Slop heap: [docs/DreamSlop.md](docs/DreamSlop.md).
