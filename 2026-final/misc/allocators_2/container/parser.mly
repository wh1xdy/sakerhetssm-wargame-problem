%{
  open Ast
%}

%token <string> IDENT
%token <int> INT
%token LET EQUALS CONST ADD MUL CHECK_ADMIN COMMA SEMICOLON EOF

%start <Ast.program> prog
%%

prog:
  | stmts = list(stmt); EOF { stmts }

stmt:
  | LET; v = IDENT; EQUALS; rhs = rhs; SEMICOLON { Let(v, rhs) }

rhs:
  | CONST; n = INT { RConst n }
  | ADD; v1 = IDENT; COMMA; v2 = IDENT { RAdd(v1, v2) }
  | MUL; v1 = IDENT; COMMA; v2 = IDENT { RMul(v1, v2) }
  | CHECK_ADMIN; v = IDENT { RCheckAdmin v }
