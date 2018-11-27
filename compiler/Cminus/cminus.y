/****************************************************/
/* File: tiny.y                                     */
/* The TINY Yacc/Bison specification file           */
/* Compiler Construction: Principles and Practice   */
/* Kenneth C. Louden                                */
/****************************************************/
%{
#define YYPARSER /* distinguishes Yacc output from other code files */

#include "globals.h"
#include "util.h"
#include "scan.h"
#include "parse.h"

#define YYSTYPE TreeNode *
static char * savedName; /* for use in assignments */
static int savedNumber;
static int savedLineNo;  /* ditto */
static TreeNode * savedTree; /* stores syntax tree for later return */
static int yylex(void); // added 11/2/11 to ensure no conflict with lex
static int yyerror(char * message);

%}

%token IF ELSE WHILE RETURN INT VOID
%token ID NUM 
%token ASSIGN EQ NE LT LE GT GE PLUS MINUS TIMES OVER LPAREN RPAREN LBRACE RBRACE LCURLY RCURLY SEMI COMMA
%token ERROR 

%% /* Grammar for TINY */

program     : decl_list { savedTree = $1; }
            ;
decl_list   : decl_list decl
                 { YYSTYPE t = $1;
                   if (t != NULL)
                   { while (t->sibling != NULL)
                        t = t->sibling;
                     t->sibling = $2;
                     $$ = $1; }
                     else $$ = $2;
                 }
            | decl   { $$ = $1; }
            ;

decl        : var_decl   { $$ = $1; }
            | func_decl    { $$ = $1; }
            ;
var_decl    : type_spec saveName SEMI
                  { $$ = newDeclNode(VarDeclK);
                    $$->attr.name = savedName;
                    $$->lineno = savedLineNo;
                    $$->child[0] = $1;
                  }
            | type_spec saveName LBRACE saveNumber RBRACE SEMI
                  { $$ = newDeclNode(ArrDeclK); 
                    $$->attr.array.name = savedName;
                    $$->attr.array.size = savedNumber;
                    $$->lineno = savedLineNo;
                    $$->child[0] = $1;
                  }
            ;
func_decl   : type_spec saveName 
                  {  $$ = newDeclNode(FuncDeclK);
                     $$->attr.name = savedName;
                     $$->lineno = savedLineNo;
                  } 
              LPAREN params RPAREN comp_stmt
                   { $$ = $3;
                     $$->child[0] = $1;
                     $$->child[1] = $5;
                     $$->child[2] = $7;
                   }
            ;
type_spec   : INT  { $$  = newTypeNode(TypeNameK);
                     $$->attr.type = INT; }
            | VOID  { $$  = newTypeNode(TypeNameK);
                     $$->attr.type = VOID; }
            ;
params      : param_list { $$ = $1; }
            /*| VOID  { $$  = newTypeNode(TypeNameK);
                     $$->attr.type = VOID; }*/
            ;
param_list  : param_list COMMA param
                 { YYSTYPE t = $1;
                   if (t != NULL)
                   { while (t->sibling != NULL)
                        t = t->sibling;
                     t->sibling = $3;
                     $$ = $1; }
                     else $$ = $3;
                 }
            | param   { $$ = $1; }
            ;
param       : type_spec saveName
                 { $$ = newParamNode(SingleParamK);
                   $$->child[0] = $1;
                   $$->attr.name = savedName;
                   $$->lineno = savedLineNo;
                 }
            | type_spec saveName LBRACE RBRACE
                 { $$ = newParamNode(ArrParamK);
                   $$->attr.name = savedName;
                   $$->lineno = savedLineNo;
                   $$->child[0] = $1;
                 }
            | type_spec
                 {
                  $$ = newParamNode(SingleParamK);
                  $$->child[0] = $1;
                  $$->attr.name = NULL;
                  $$->lineno = lineno;
                 }
            ;
comp_stmt   : LCURLY local_decls stmt_list RCURLY
                 { $$ = newStmtNode(CompK);
                   $$->child[0] = $2;
                   $$->child[1] = $3;
                 }
            ;
local_decls : local_decls var_decl
                 { YYSTYPE t = $1;
                   if (t != NULL)
                   { while (t->sibling != NULL)
                        t = t->sibling;
                     t->sibling = $2;
                     $$ = $1; }
                     else $$ = $2;
                 }
            | /* empty */ { $$ = NULL; }
            ;
stmt_list   : stmt_list stmt
                 { YYSTYPE t = $1;
                   if (t != NULL)
                   { while (t->sibling != NULL)
                        t = t->sibling;
                     t->sibling = $2;
                     $$ = $1; }
                     else $$ = $2;
                 }
            | /* empty */ { $$ = NULL; }
            ;
stmt        : exp_stmt { $$ = $1; }
            | selec_stmt { $$ = $1; }
            | comp_stmt { $$ = $1; }
            | iter_stmt { $$ = $1; }
            | return_stmt { $$ = $1; }
            ;
exp_stmt    : exp SEMI
                 { $$ = $1; }
            | SEMI
                 { $$ = NULL; }
            ;
selec_stmt  : IF LPAREN exp RPAREN stmt
                 { $$ = newStmtNode(IfK);
                   $$->child[0] = $3;
                   $$->child[1] = $5;
                 }
            | IF LPAREN exp RPAREN stmt ELSE stmt
                 { $$ = newStmtNode(IfK);
                   $$->child[0] = $3;
                   $$->child[1] = $5;
                   $$->child[2] = $7;
                 }
            ;
iter_stmt   : WHILE LPAREN exp RPAREN stmt
                 { $$ = newStmtNode(IterK);
                   $$->child[0] = $3;
                   $$->child[1] = $5;
                 }
            ;
return_stmt : RETURN SEMI
                 { $$ = newStmtNode(ReturnK);
                   $$->attr.type = VOID;
                 }
            | RETURN exp SEMI
                 { $$ = newStmtNode(ReturnK);
                   $$->child[0] = $2;
                 }
            ;
exp         : var ASSIGN exp
                 { $$ = newExpNode(AssignK);
                   $$->child[0] = $1;
                   $$->child[1] = $3;
                 }
            | simple_exp { $$ = $1; }
            ;
simple_exp  : add_exp EQ add_exp
                 { $$ = newExpNode(OpK);
                   $$->child[0] = $1;
                   $$->child[1] = $3;
                   $$->attr.op = EQ;
                 }
            | add_exp NE add_exp
                 { $$ = newExpNode(OpK);
                   $$->child[0] = $1;
                   $$->child[1] = $3;
                   $$->attr.op = NE;
                 }
            | add_exp LT add_exp
                 { $$ = newExpNode(OpK);
                   $$->child[0] = $1;
                   $$->child[1] = $3;
                   $$->attr.op = LT;
                 }
            | add_exp LE add_exp
                 { $$ = newExpNode(OpK);
                   $$->child[0] = $1;
                   $$->child[1] = $3;
                   $$->attr.op = LE;
                 }
            | add_exp GT add_exp
                 { $$ = newExpNode(OpK);
                   $$->child[0] = $1;
                   $$->child[1] = $3;
                   $$->attr.op = GT;
                 }
            | add_exp GE add_exp
                 { $$ = newExpNode(OpK);
                   $$->child[0] = $1;
                   $$->child[1] = $3;
                   $$->attr.op = GE;
                 }
            | add_exp { $$ = $1; }
            ;
add_exp     : add_exp PLUS term 
                 { $$ = newExpNode(OpK);
                   $$->child[0] = $1;
                   $$->child[1] = $3;
                   $$->attr.op = PLUS;
                 }
            | add_exp MINUS term
                 { $$ = newExpNode(OpK);
                   $$->child[0] = $1;
                   $$->child[1] = $3;
                   $$->attr.op = MINUS;
                 } 
            | term { $$ = $1; }
            ;
term        : term TIMES factor 
                 { $$ = newExpNode(OpK);
                   $$->child[0] = $1;
                   $$->child[1] = $3;
                   $$->attr.op = TIMES;
                 }
            | term OVER factor
                 { $$ = newExpNode(OpK);
                   $$->child[0] = $1;
                   $$->child[1] = $3;
                   $$->attr.op = OVER;
                 }
            | factor { $$ = $1; }
            ;
factor      : LPAREN exp RPAREN
                 { $$ = $2; }
            | NUM
                 { $$ = newExpNode(ConstK);
                   $$->attr.val = atoi(tokenString);
                 }
            | var { $$ = $1; }
            | call { $$ = $1; }
            ;
var         : saveName { 
                   $$ = newExpNode(IdK);
                   $$->attr.name = savedName;
                 }
            | saveName { 
                   $$  = newExpNode(ArrIdK);
                   $$->attr.name = savedName;
                 }
              LBRACE exp RBRACE
                 {  $$ = $2;
                    $$->child[0] = $4;
                 }
call        : saveName 
                 { $$ = newExpNode(CallK);
                   $$->attr.name = savedName;
                   $$->lineno = lineno;
                 }
              LPAREN args RPAREN
                 { $$ = $2;
                   $$->child[0] = $4; 
                 }
            ;
args        : arg_list { $$ = $1; }
            | /* empty */ { $$ = NULL; }
            ;
arg_list    : arg_list COMMA exp
                 { YYSTYPE t = $1;
                   if (t != NULL)
                   { while (t->sibling != NULL)
                        t = t->sibling;
                     t->sibling = $3;
                     $$ = $1; }
                     else $$ = $3;
                 }
            | exp   { $$ = $1; }
            ;
saveName    : ID { savedName = copyString(tokenString); 
                   savedLineNo = lineno;
                 }
            ;
saveNumber : NUM { savedNumber = atoi(tokenString);
                    savedLineNo = lineno; 
                  }
            ;
%%

int yyerror(char * message)
{ fprintf(listing,"Syntax error at line %d: %s\n",lineno,message);
  fprintf(listing,"Current token: ");
  printToken(yychar,tokenString);
  Error = TRUE;
  return 0;
}

/* yylex calls getToken to make Yacc/Bison output
 * compatible with ealier versions of the TINY scanner
 */
static int yylex(void)
{ return getToken(); }

TreeNode * parse(void)
{ yyparse();
  return savedTree;
}

