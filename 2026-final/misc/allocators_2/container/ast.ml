(* Source-level variable name used in SSA bindings. *)
type var_id = string

(* Right-hand-side expression forms supported by the language. *)
type rhs =
  (* Integer literal. *)
  | RConst of int
  (* Binary arithmetic over two previously defined variables. *)
  | RAdd of var_id * var_id
  (* Binary multiplication over two previously defined variables. *)
  | RMul of var_id * var_id
  (* Unary privileged check operation over one variable. *)
  | RCheckAdmin of var_id

(* One SSA statement: bind a variable to an expression. *)
type stmt =
  | Let of var_id * rhs

(* Program is an ordered list of let-bindings. *)
type program = stmt list
