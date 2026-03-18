exception Parse_error of Lexing.position

let parse_channel ic =
  let lexbuf = Lexing.from_channel ic in
  try Parser.prog Lexer.read lexbuf
  with Parser.Error -> raise (Parse_error lexbuf.Lexing.lex_curr_p)

let parse_string s =
  let lexbuf = Lexing.from_string s in
  try Parser.prog Lexer.read lexbuf
  with Parser.Error -> raise (Parse_error lexbuf.Lexing.lex_curr_p)

let read_exactly ic len =
  let buf = Bytes.create len in
  really_input ic buf 0 len;
  Bytes.unsafe_to_string buf

let parse_length_prefixed_stdin () =
  let header = input_line stdin in
  let len =
    try int_of_string (String.trim header)
    with Failure _ ->
      failwith "Invalid stdin header: expected decimal payload length"
  in
  if len < 0 then failwith "Invalid stdin header: negative payload length";
  let payload = read_exactly stdin len in
  parse_string payload

let print_parse_error pos =
  Printf.eprintf "Parse error at line %d, column %d\n"
    pos.Lexing.pos_lnum
    (pos.Lexing.pos_cnum - pos.Lexing.pos_bol)

let digest_hex s = Digest.string s |> Digest.to_hex

let canonical_file = "program/canonical.ssa"
let fixed_reg_count = 11
let fixed_admin_token = 31337
let flag_value () = Sys.getenv "FLAG"

let canonical_hash_of_ast ast =
  let lowered = Dag.of_ast ast in
  Dag.canonical_string lowered.dag |> digest_hex

let verify_hash_ast submission_ast =
  let canonical_ast =
    let ic = open_in_bin canonical_file in
    Fun.protect
      ~finally:(fun () -> close_in_noerr ic)
      (fun () -> parse_channel ic)
  in
  let canonical_hash = canonical_hash_of_ast canonical_ast in
  let submission_hash = canonical_hash_of_ast submission_ast in
  (canonical_hash, submission_hash, String.equal canonical_hash submission_hash)

let compile_ast submission_ast =
  let canonical_hash, submission_hash, ok = verify_hash_ast submission_ast in
  if not ok then (
    Printf.printf "hash_ok=false\ncanonical_hash=%s\nsubmission_hash=%s\n" canonical_hash submission_hash;
    exit 2
  );
  let lowered = Dag.of_ast submission_ast in
  Dag.validate_schedule lowered.op_id_to_node lowered.dag.root_op_id lowered.source_schedule;
  let alloc =
    Regalloc.allocate
      ~reg_count:fixed_reg_count
      ~schedule:lowered.source_schedule
      ~nodes:lowered.op_id_to_node
  in
  let result =
    Regalloc.execute
      lowered.dag
      alloc.reg_assign
      alloc.insts
      ~admin_token:fixed_admin_token
      ~reg_count:fixed_reg_count
  in
  Printf.printf "hash_ok=true\ncanonical_hash=%s\nsubmission_hash=%s\n" canonical_hash submission_hash;
  Printf.printf "result=%d\n" result;
  let is_admin = result = fixed_admin_token in
  Printf.printf "admin=%s\n" (if is_admin then "true" else "false");
  if is_admin then Printf.printf "flag=%s\n" (flag_value ())

let usage argv0 =
  Printf.eprintf "Usage:\n  %s\n  <len>\\n<payload-bytes> on stdin\n" argv0;
  exit 1

let run () =
  let argc = Array.length Sys.argv in
  if argc = 1 then (
    Printf.printf "What are allocators?...\n%!";
    compile_ast (parse_length_prefixed_stdin ())
  ) else usage Sys.argv.(0)

let () =
  try run () with
  | Parse_error pos ->
      print_parse_error pos;
      exit 1
  | Dag.Error msg ->
      prerr_endline ("AST error: " ^ msg);
      exit 1
  | Failure msg ->
      prerr_endline ("Failure: " ^ msg);
      exit 1
  | Sys_error msg ->
      prerr_endline msg;
      exit 1
  | End_of_file ->
      prerr_endline "Unexpected EOF while reading stdin payload";
      exit 1
