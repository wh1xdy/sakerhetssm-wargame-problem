open Dag

type inst = {
  (* Original DAG node for this scheduled instruction. *)
  op : op_node;
  (* Physical register written by this instruction. *)
  reg : int;
}

type alloc_result = {
  (* op_id -> register assignment used by execute. *)
  reg_assign : int IntMap.t;
  (* Scheduled instruction stream with attached registers. *)
  insts : inst list;
}

let intmap_get = get_int_map_or_error

(* Executes lowered instructions against a concrete register assignment.
   The model is intentionally simple: each op reads dependency registers,
   computes a value, then writes to its destination register. *)
let execute (prog : Dag.t) (reg_assign : int IntMap.t) (insts : inst list) ~(admin_token : int) ~(reg_count : int)
  : int =
  let regs = Array.make reg_count 0 in
  let load op_id =
    let reg = intmap_get reg_assign op_id in
    regs.(reg)
  in
  List.iter
    (fun inst ->
       let value =
         match inst.op.kind, inst.op.deps with
         | OpConst n, [] -> n
         | OpAdd, [d1; d2] -> load d1 + load d2
         | OpMul, [d1; d2] -> load d1 * load d2
         | OpCheckAdmin, [d1] -> if load d1 = admin_token then admin_token else 0
         | _ -> failwith "invalid instruction"
       in
       regs.(inst.reg) <- value)
    insts;
  let root_reg = intmap_get reg_assign prog.root_op_id in
  regs.(root_reg)

(* Direct-mapping allocator.
   Each op_id is mapped to a register with op_id mod reg_count, so assignment
   is schedule-independent while emitted instructions still follow schedule
   order. *)
let allocate ~(reg_count : int) ~(schedule : op_id list)
    ~(nodes : op_node IntMap.t) : alloc_result =
  let reg_assign = ref IntMap.empty in
  let insts =
    List.map
      (fun op_id ->
         let op = intmap_get nodes op_id in
         let reg = op_id mod reg_count in
         reg_assign := IntMap.add op_id reg !reg_assign;
         { op; reg })
      schedule
  in
  { reg_assign = !reg_assign; insts }
