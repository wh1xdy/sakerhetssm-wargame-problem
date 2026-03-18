{
  open Parser
}

let white = [' ' '\t' '\n' '\r']+
let digit = ['0'-'9']
let id = ['a'-'z' 'A'-'Z' '_'] ['a'-'z' 'A'-'Z' '0'-'9' '_']*

rule read = parse
  | white { read lexbuf }
  | "let" { LET }
  | "="      { EQUALS }
  | "const"  { CONST }
  | "add"    { ADD }
  | "mul"    { MUL }
  | "check_admin" { CHECK_ADMIN }
  | ","      { COMMA }
  | ";"      { SEMICOLON }
  | digit+ as n { INT (int_of_string n) }
  | id as s  { IDENT s }
  | eof      { EOF }
