/****************************************************/
/* File: analyze.c                                  */
/* Semantic analyzer implementation                 */
/* for the TINY compiler                            */
/* Compiler Construction: Principles and Practice   */
/* Kenneth C. Louden                                */
/****************************************************/

#include "globals.h"
#include "symtab.h"
#include "analyze.h"

#define SIZE 211

/* counter for variable memory locations */
/* stack for scope names */

/* Procedure traverse is a generic recursive 
 * syntax tree traversal routine:
 * it applies preProc ip preorder and postProc 
 * in postorder to tree pointed to by t
 */

static ExpType curFuncType;
static int preserve = FALSE;
static int elseCheck = FALSE;
static char *scopeName;
static void traverse( TreeNode * t,
               void (* preProc) (TreeNode *),
               void (* postProc) (TreeNode *) )
{ if (t != NULL)
  { preProc(t);
    int i;
    for (i=0; i < MAXCHILDREN; i++) {
      traverse(t->child[i],preProc,postProc);
    }
    postProc(t);
    traverse(t->sibling,preProc,postProc);
  }
}

void insertBuiltin() {
  ss_push("global", 0);

  TreeNode *func;
  TreeNode *typeSpec;
  TreeNode *param;
  TreeNode *compStmt;

  // input()
  func = newDeclNode(FuncDeclK);
  func->type = Integer;
  typeSpec = newTypeNode(TypeNameK);
  typeSpec->attr.type = INT;
  
  
  compStmt = newStmtNode(CompK);
  compStmt->child[0] = NULL;
  compStmt->child[1] = NULL;

  func->lineno = 0;
  func->attr.name = "input";
  func->child[0] = typeSpec;
  func->child[1] = NULL;
  func->child[2] = compStmt;
  func->scope = "global";

  ss_bucket_add("input", Integer, 0, func);

  // output()
  func = newDeclNode(FuncDeclK);
  func->type = Void;
  typeSpec = newTypeNode(TypeNameK);
  typeSpec->attr.type = VOID;
  
  param = newParamNode(SingleParamK);
  param->attr.name = "arg";
  param->type = Integer;
  param->child[0] = newTypeNode(TypeNameK);
  param->child[0]->attr.type = INT;

  compStmt = newStmtNode(CompK);
  compStmt->child[0] = NULL;
  compStmt->child[1] = NULL;

  func->lineno = 0;
  func->attr.name = "output";
  func->child[0] = typeSpec;
  func->child[1] = param;
  func->child[2] = compStmt;
  func->scope = "global";

  ss_bucket_add("output", Void, 0, func);
}

/* Procedure insertNode inserts 
 * identifiers stored in t into 
 * the symbol table 
 */

char* getName(char *funcName) {
  char *tag = (char*)malloc(strlen(funcName));
  strcpy(tag, funcName);
  char *buf = (char*)malloc(strlen(ss_top()->name));
  strcpy(buf, ss_top()->name);
  strcat(buf, tag);
  return buf;
}

static void symbolError(TreeNode * t, char * message)
{ 
  if(t->attr.name != NULL) {
    fprintf(listing,"error: %s %s at line %d\n",message,t->attr.name,t->lineno);
    Error = TRUE;
  }
  else {
    fprintf(listing,"error: %s %s at line %d\n",message,t->attr.array.name,t->lineno);
    Error = TRUE;
  }
}

static void insertList( TreeNode * t)
{ switch (t->nodekind)
  { case StmtK: {
      switch (t->kind.stmt)
      { case CompK: {
          t->scope = ss_top()->name;
          if(preserve) 
            preserve = FALSE;
          else 
            ss_push(scopeName, t->lineno);
          break;
        }
        case IterK: {
          if(t->child[1]->kind.stmt == CompK) 
            scopeName = getName(":while");
          break;
        }
        case IfK: {
          if(t->child[1]->kind.stmt == CompK) 
            scopeName = getName(":if");
          if(t->child[2] != NULL && t->child[2]->kind.stmt == CompK)  
            elseCheck = TRUE;
          break;
        }
        default:
          break;
      }
      break;
    }
    case ExpK: {
      switch (t->kind.exp)
      { case IdK: {
          if(ss_lookup(t->attr.name) != NULL)
            ss_line_add(t->attr.name, t->lineno, t);
          else 
            symbolError(t, "Undeclared variable");
          break;
        }
        case ArrIdK: {
          if(ss_lookup(t->attr.array.name) != NULL) 
            ss_line_add(t->attr.array.name, t->lineno, t);
          else 
            symbolError(t, "Undeclared variable");
          break;
        }
        case CallK: {
          if(ss_lookup(t->attr.name) != NULL) {
            ss_line_add(t->attr.name, t->lineno, t);
            TreeNode *arg = t->child[0];

            if(arg != NULL && arg->attr.name != NULL) { 
              if(ss_lookup(arg->attr.name) == NULL) 
                symbolError(t, "Undeclared variable");
              else 
                arg = arg->sibling;
            }
            else if(arg != NULL && arg->attr.array.name != NULL) { 
              if(ss_lookup(arg->attr.array.name) == NULL) 
                symbolError(t, "Undeclared variable");
              else 
                arg = arg->sibling;
            }
          } else {
            symbolError(t, "Undeclared function");
          }
          break;
        }
        default:
          break;
      }
      break;
    }
    case DeclK: {
      switch (t->kind.decl)
      { case FuncDeclK: {
          if (ss_lookup_excluding_parent(t->attr.name) == NULL) {
            if(t->child[0]->attr.type == INT) 
              t->type = Integer;
            else if(t->child[0]->attr.type == VOID) 
              t->type = Void;
            
            ss_bucket_add(t->attr.name, t->type, t->lineno, t);
            t->scope = ss_top()->name;

            ss_push(t->attr.name, t->lineno);
            preserve = TRUE;
          } else {
            symbolError(t, "Duplicated function name");
          }
          break;
        }
        case VarDeclK: {
          if (ss_lookup_excluding_parent(t->attr.name) == NULL) {
            if(t->child[0]->attr.type == INT) 
              t->type = Integer;
            else if(t->child[0]->attr.type == VOID) 
              symbolError(t, "Variable type cannot be Void");
        
            ss_bucket_add(t->attr.name, t->type, t->lineno, t);
            t->scope = ss_top()->name;
          } else {
            symbolError(t, "Duplicated variable name");
          }
          break;
        }
        case ArrDeclK: {
          if (ss_lookup_excluding_parent(t->attr.array.name) == NULL) {
            if(t->child[0]->attr.type == INT) 
              t->type = IntegerArray;
            else if(t->child[0]->attr.type == VOID) 
              symbolError(t, "Variable type cannot be Void");

            ss_bucket_add(t->attr.array.name, t->type, t->lineno, t);
            t->scope = ss_top()->name;
          } else {
            symbolError(t, "Duplicated variable name");
          }
          break;
        }
        default:
          break;
      }
      break;
    }
    case ParamK: 
      switch(t->kind.param) {
        case SingleParamK: {
          if(t->attr.name != NULL) {
            if(t->child[0]->attr.type == INT) 
              t->type = Integer;

            if (ss_lookup_excluding_parent(t->attr.name) == NULL) {
              ss_bucket_add(t->attr.name, t->type, t->lineno, t);
              t->scope = ss_top()->name;
            } else {
              symbolError(t, "Duplicated parameter name");
            }
          }
          break;
        }
        case ArrParamK: {
          if(t->attr.array.name != NULL) {
            if(t->child[0]->attr.type == INT) 
             t->type = IntegerArray;

            if (ss_lookup_excluding_parent(t->attr.array.name) == NULL) {
              ss_bucket_add(t->attr.array.name, t->type, t->lineno, t);
              t->scope = ss_top()->name;
            } else {
              symbolError(t, "Duplicated parameter name");
            }
          }
          break;
        }
        default:
          break;
      }
      break;
    default:
      break;
  }
}

static void postInsertList(TreeNode *t) 
{ switch(t->nodekind) 
  { case StmtK:
      switch(t->kind.stmt)
      { case CompK:
          st_insert();

          if(elseCheck) {
            ss_push(getName(":else"), t->lineno);
            elseCheck = FALSE;
            preserve = TRUE;
          }
          break;
      }
      break;
  }
}

/* Function buildSymtab constructs the symbol 
 * table by preorder traversal of the syntax tree
 */
void buildSymtab(TreeNode * syntaxTree)
{ insertBuiltin();
  traverse(syntaxTree,insertList,postInsertList);
  st_insert();
  if (TraceAnalyze && !Error)
  { printSymTab(listing);
  }
}

static void typeError(TreeNode * t, char * message)
{ fprintf(listing,"Type error at line %d: %s\n",t->lineno,message);
  Error = TRUE;
}

static void preCheckList(TreeNode * t)
{ switch (t->nodekind)
  { case DeclK:
      switch (t->kind.decl)
      { case FuncDeclK:
          if(t->child[0]->attr.type == INT) {
            curFuncType = Integer;
          } else if(t->child[0]->attr.type == VOID) {
            curFuncType = Void;
          }
          break;
        default:
          break;
      }
      break;
    default:
      break;
  }
}

/* Procedure checkNode performs
 * type checking at a single tree node
 */
static void checkList(TreeNode * t)
{ switch (t->nodekind)
  { case StmtK: {
      switch (t->kind.stmt)
      { case IterK: {
          if (t->child[0]->type == Void)
            typeError(t->child[0],"while test has void value");
          break;
        }
        case ReturnK: {
          TreeNode* expr = t->child[0];
          if (curFuncType == Void &&
            (expr != NULL && expr->type != Void)) {
            typeError(t,"return type inconsistance");
          } else if (curFuncType == Integer &&
            (expr == NULL || expr->type != Integer)) {
            typeError(t,"return type inconsistance");
          }
          break;
        }
        default:
          break;
      }
      break;
    }
    case ExpK: {
      switch (t->kind.exp)
      { case AssignK: {
          if (t->child[0]->type == IntegerArray)
          /* no value can be assigned to array variable */
            typeError(t->child[0], "assignment type inconsistance");
          else if (t->child[1]->type == Void)
          /* r-value cannot have void type */
            typeError(t->child[0],"r-value cannot be void type");
          break;
        }
        case OpK: {
          ExpType leftType, rightType;
          TokenType op;

          if(t->child[0]->attr.type == INT) leftType = Integer;

          leftType = t->child[0]->type;
          rightType = t->child[1]->type;
          op = t->attr.op;

          if(leftType == Void || rightType == Void) 
            typeError(t,"operands type cannot be void");
          else if(leftType != rightType)
            typeError(t, "operands types inconsistance");
          else 
            t->type = Integer;
          break;
        }
        case ConstK: {
          t->type = Integer;
          break;
        }
        case ArrIdK: {
          if(t->child[0]->type != Integer)
            typeError(t, "index expression should have integer type");
          else 
            t->type = Integer;
          break;
        }
        case CallK: {
          TreeNode * funcDecl = st_lookup(t->scope, t->attr.name)->treeNode;
          TreeNode *arg;
          TreeNode *param;

          arg = t->child[0];
          param = funcDecl->child[1];

          while (arg != NULL) { 
            /* the number of arguments does not match tothat of parameters */
            if (param == NULL)
              typeError(arg,"invalid function call");
            else if(arg->type != param->type) 
              typeError(arg,"invalid function call");
            else {  
              arg = arg->sibling;
              param = param->sibling;
              continue;
            }
            break;
          }
          /* the number of arguments does not match to that of parameters */
          if (arg == NULL && param != NULL)
            
            typeError(t,"invalid function parameters");
          break;
        }
        default:
          break;
      }
      break;
    }
    default:
      break;
  }
}

/* Procedure typeCheck performs type checking 
 * by a postorder syntax tree traversal
 */
void typeCheck(TreeNode * syntaxTree)
{ traverse(syntaxTree,preCheckList,checkList);
}
