open Ast

(* String-keyed collections for variable names. *)
module StringMap = Map.Make (String)
(* Int-keyed collections for operation ids. *)
module IntMap = Map.Make (struct
  type t = int
  let compare = compare
end)
module IntSet = Set.Make (struct
  type t = int
  let compare = compare
end)

(* Stable integer id used for operation nodes in the DAG. *)
type op_id = int

(* Operation type for each DAG node (structure is carried in deps). *)
type op_kind =
  | OpConst of int
  | OpAdd
  | OpMul
  | OpCheckAdmin

(* One operation in the dependency graph. deps points to parent op ids. *)
type op_node = {
  id : op_id;
  kind : op_kind;
  deps : op_id list;
}

(* Final lowered program:
   - root_op_id: id of the output operation
   - topo_ops: operations sorted so deps always come first *)
type t = {
  root_op_id : op_id;
  topo_ops : op_node list;
}

(* Rich lowering output used by later stages (hashing, register allocation). *)
type lowered = {
  dag : t;
  op_id_to_node : op_node IntMap.t;
  source_schedule : op_id list;
}

(* User-facing errors emitted during AST validation/lowering. *)
exception Error of string

(* Helper lookups that raise a domain-specific error with context. *)
let get_string_map_or_error map key =
  match StringMap.find_opt key map with
  | Some value -> value
  | None -> raise (Error ("Undefined variable " ^ key))

let get_int_map_or_error map key =
  match IntMap.find_opt key map with
  | Some value -> value
  | None -> raise (Error "Internal error: missing operation node")

(* Variables referenced by one RHS expression. *)
let rhs_deps = function
  | RConst _ -> []
  | RAdd (v1, v2) | RMul (v1, v2) -> [v1; v2]
  | RCheckAdmin v -> [v]

(* Translate parsed RHS syntax into a DAG operation kind. *)
let rhs_kind = function
  | RConst n -> OpConst n
  | RAdd _ -> OpAdd
  | RMul _ -> OpMul
  | RCheckAdmin _ -> OpCheckAdmin

(* Collect all let-definitions, reject duplicates, and choose last let as output variable. *)
let read_definitions (stmts : Ast.program) =
  let _defs, rev_defs, root_var =
    List.fold_left
      (fun (defs, rev_defs, _) stmt ->
         match stmt with
         | Let (name, rhs) ->
             if StringMap.mem name defs then
               raise (Error ("Duplicate definition for variable " ^ name));
             (StringMap.add name rhs defs, (name, rhs) :: rev_defs, Some name))
      (StringMap.empty, [], None)
      stmts
  in
  let root_var =
    match root_var with
    | Some name -> name
    | None -> raise (Error "Program is empty; expected at least one let binding")
  in
  (List.rev rev_defs, root_var)

(* Add edge dep -> child (child depends on dep). *)
let add_edge edges dep_id child_id =
  let current =
    match IntMap.find_opt dep_id edges with
    | Some out -> out
    | None -> []
  in
  IntMap.add dep_id (child_id :: current) edges

(* Build:
   - `edges`: dependency adjacency list (dep -> list of dependents)
   - `op_nodes`: node payload by op id *)
let build_graph indexed_defs var_to_op_id =
  let edges, op_nodes =
    List.fold_left
      (fun (edges, op_nodes) (id, _, rhs) ->
         let deps =
           List.map
             (fun dep_var -> get_string_map_or_error var_to_op_id dep_var)
             (rhs_deps rhs)
         in
         let node = { id; kind = rhs_kind rhs; deps } in
         let edges =
           List.fold_left
             (fun acc dep_id -> add_edge acc dep_id id)
             edges
             deps
         in
         (edges, IntMap.add id node op_nodes))
      (IntMap.empty, IntMap.empty)
      indexed_defs
  in
  (IntMap.map (fun out -> List.sort compare out) edges, op_nodes)

(* Deterministic topological sort via DFS postorder + reverse.
   `path` tracks active recursion frames for cycle detection. *)
let topo_sort indexed_defs edges =
  let rec visit path visited postorder id =
    if IntSet.mem id visited then
      (visited, postorder)
    else if IntSet.mem id path then
      raise (Error "Operation graph contains a cycle; topological sorting failed")
    else
      let path = IntSet.add id path in
      let children =
        match IntMap.find_opt id edges with
        | Some out -> out
        | None -> []
      in
      let visited, postorder =
        List.fold_left
          (fun (visited, postorder) child_id ->
             visit path visited postorder child_id)
          (visited, postorder)
          children
      in
      (IntSet.add id visited, id :: postorder)
  in
  (* For stable canonical output: visit larger ids first, then reverse postorder. *)
  let all_ids_desc =
    List.map (fun (id, _, _) -> id) indexed_defs
    |> List.sort (fun a b -> compare b a)
  in
  let visited, postorder =
    List.fold_left
      (fun (visited, postorder) id ->
         visit IntSet.empty visited postorder id)
      (IntSet.empty, [])
      all_ids_desc
  in
  if IntSet.cardinal visited <> List.length indexed_defs then
    raise (Error "Operation graph contains a cycle; topological sorting failed");
  List.rev postorder

(* Shared lowering pipeline used by of_ast. *)
let lower (stmts : Ast.program) =
  let ordered_defs, root_var = read_definitions stmts in
  let all_defs = List.sort (fun (n1, _) (n2, _) -> String.compare n1 n2) ordered_defs in
  let indexed_defs = List.mapi (fun id (name, rhs) -> (id, name, rhs)) all_defs in
  let var_to_op_id =
    List.fold_left
      (fun acc (id, name, _) -> StringMap.add name id acc)
      StringMap.empty
      indexed_defs
  in
  let root_op_id = get_string_map_or_error var_to_op_id root_var in
  let edges, op_nodes = build_graph indexed_defs var_to_op_id in
  let sorted_ids = topo_sort indexed_defs edges in
  let topo_ops = List.map (fun id -> get_int_map_or_error op_nodes id) sorted_ids in
  let source_schedule =
    List.filter_map
      (fun (name, _) ->
         match StringMap.find_opt name var_to_op_id with
         | Some id -> Some id
         | None -> None)
      ordered_defs
  in
  let dag = { root_op_id; topo_ops } in
  (dag, op_nodes, source_schedule)

(* Lower with extra bookkeeping: operation map and source order. *)
let of_ast (stmts : Ast.program) : lowered =
  let dag, op_nodes, source_schedule = lower stmts in
  { dag; op_id_to_node = op_nodes; source_schedule }

(* Check that a provided schedule is a valid topological order for the DAG,
   and that the root operation is executed last. *)
let validate_schedule (nodes : op_node IntMap.t) (root_op_id : op_id) (schedule : op_id list) : unit =
  let seen = ref IntSet.empty in
  List.iter
    (fun id ->
       if IntSet.mem id !seen then
         raise (Error "Schedule contains duplicate operation ids");
       let node = get_int_map_or_error nodes id in
       List.iter
         (fun dep ->
            if not (IntSet.mem dep !seen) then
              raise (Error "Schedule is not a valid topological order"))
         node.deps;
       seen := IntSet.add id !seen)
    schedule;
  let expected = IntMap.cardinal nodes in
  if IntSet.cardinal !seen <> expected then
    raise (Error "Schedule does not cover all operations");
  match List.rev schedule with
  | [] -> raise (Error "Schedule is empty")
  | last :: _ ->
      if last <> root_op_id then
        raise (Error "Schedule must execute root operation last")

(* Canonical textual form of a DAG used for hashing. *)
let string_of_op_node (node : op_node) =
  match node.kind, node.deps with
  | OpConst n, [] -> Printf.sprintf "#%d = Const(%d)" node.id n
  | OpAdd, [d1; d2] -> Printf.sprintf "#%d = Add(#%d, #%d)" node.id d1 d2
  | OpMul, [d1; d2] -> Printf.sprintf "#%d = Mul(#%d, #%d)" node.id d1 d2
  | OpCheckAdmin, [d1] -> Printf.sprintf "#%d = CheckAdmin(#%d)" node.id d1
  | _ -> Printf.sprintf "#%d = <invalid>" node.id

let canonical_string (prog : t) =
  let lines = List.map string_of_op_node prog.topo_ops in
  let lines = lines @ [Printf.sprintf "root = #%d" prog.root_op_id] in
  String.concat "\n" lines
