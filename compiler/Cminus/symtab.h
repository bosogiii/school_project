/****************************************************/
/* File: symtab.h                                   */
/* Symbol table interface for the TINY compiler     */
/* (allows only one symbol table)                   */
/* Compiler Construction: Principles and Practice   */
/* Kenneth C. Louden                                */
/****************************************************/

#ifndef _SYMTAB_H_
#define _SYMTAB_H_

/* Procedure st_insert inserts line numbers and
 * memory locations into the symbol table
 * loc = memory location is inserted only the
 * first time, otherwise ignored
 */
#define SIZE 211
#include "globals.h"


/* the list of line numbers of the source 
 * code in which a variable is referenced
 */
typedef struct LineListRec
   { int lineno;
     struct LineListRec * next;
   } * LineList;

/* The record in the bucket lists for
 * each variable, including name, 
 * assigned memory location, and
 * the list of line numbers in which
 * it appears in the source code
 */

typedef struct BucketListRec
   { char * name;
     ExpType type;
     LineList lines;
     TreeNode *treeNode;
     int memloc ; /* memory location for variable */
     struct BucketListRec * next;
   } * BucketList;

typedef struct ScopeListRec
   { char * name;
     int loc;
     int startLineNo;
     int endLineNo;
     BucketList bucket[SIZE];
     struct ScopeListRec * parent;
   } * ScopeList;

ScopeList ss_top();
void ss_push(char *scope, int startLineNo);
ScopeList ss_pop();

void ss_bucket_add(char *name, ExpType type, int lineno, TreeNode *t);
void ss_line_add(char *name, int lineno, TreeNode *tn);
BucketList ss_lookup(char *name);
BucketList ss_lookup_excluding_parent(char *name);

void st_insert();
BucketList st_lookup(char *scope, char *name);


// /* Procedure printSymTab prints a formatted 
//  * listing of the symbol table contents 
//  * to the listing file
//  */
void printScopeStack(FILE * listing);
void printSymTab(FILE * listing);

#endif
