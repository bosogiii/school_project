/****************************************************/
/* File: symtab.c                                   */
/* Symbol table implementation for the TINY compiler*/
/* (allows only one symbol table)                   */
/* Symbol table is implemented as a chained         */
/* hash table                                       */
/* Compiler Construction: Principles and Practice   */
/* Kenneth C. Louden                                */
/****************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "symtab.h"
#include "globals.h"

/* SIZE is the size of the hash table */


/* SHIFT is the power of two used as multiplier
   in hash function  */
#define SHIFT 4


/* the hash function */
static int hash ( char * key )
{ int temp = 0;
  int i = 0;
  while (key[i] != '\0')
  { temp = ((temp << SHIFT) + key[i]) % SIZE;
    ++i;
  }
  return temp;
}

/* 전체 symbol table*/
static ScopeList symbolTable;
/* 살아있는 scope에 대한 symbol table */
static ScopeList scopeStack;

/* Procedure st_insert inserts line numbers and
 * memory locations into the symbol table
 * loc = memory location is inserted only the
 * first time, otherwise ignored
 */

ScopeList ss_top() {
  return scopeStack;
}

void ss_push(char *scope, int startLineNo) {
  ScopeList s = (ScopeList)malloc(sizeof(struct ScopeListRec));
  s->name = scope;
  s->loc = 0;
  s->startLineNo = startLineNo;
  s->endLineNo = 0;

  s->parent = scopeStack;
  scopeStack = s;
}

ScopeList ss_pop() {
  ScopeList s = scopeStack;
  scopeStack = scopeStack->parent;
  return s;
}

void ss_bucket_add(char *name, ExpType type, int lineno, TreeNode *t) {
  int h = hash(name);
  int loc = scopeStack->loc;
  BucketList l = (BucketList)malloc(sizeof(struct BucketListRec));
  l->name = name;
  l->type = type;
  l->lines = (LineList) malloc(sizeof(struct LineListRec));
  l->lines->lineno = lineno;
  l->lines->next = NULL;
  l->memloc = loc;
  l->next = NULL;
  l->treeNode = t;

  scopeStack->loc++;

  l->next = scopeStack->bucket[h];
  scopeStack->bucket[h] = l;
}

void ss_line_add(char *name, int lineno, TreeNode *tn) {
  int h = hash(name);

  ScopeList s = scopeStack;
  while(s != NULL) {
    BucketList l = s->bucket[h];
 
    while(l != NULL && strcmp(l->name,name) != 0) 
      l = l->next;

    if(l == NULL) s = s->parent;
    else {
      LineList t = l->lines;
      while(t->next != NULL) t = t->next;
      t->next = (LineList)malloc(sizeof(struct LineListRec));
      t->next->lineno = lineno;
      t->next->next = NULL;
      tn->type = l->type;
      tn->scope = l->treeNode->scope;
      break;
    }
  }
}

BucketList ss_lookup(char *name) {
  ScopeList s = scopeStack;

  int h = hash(name);
  while(s != NULL) {
    BucketList l = s->bucket[h];
    while(l != NULL && strcmp(name,l->name) != 0) 
      l = l->next;
    if(l == NULL) s = s->parent;
    else return l;
  }
  return NULL;
}

BucketList ss_lookup_excluding_parent(char *name) {
  int h = hash(name);
  BucketList l = scopeStack->bucket[h];

  while(l != NULL && strcmp(name,l->name) != 0)
    l = l->next;
  return l;
}

void st_insert() {
  ScopeList s = ss_pop();
  s->parent = symbolTable;
  symbolTable = s;
}


BucketList st_lookup(char *scope, char *name) {
  int h = hash(name);
  ScopeList s = symbolTable;
  BucketList l = NULL;
  while(s != NULL && strcmp(scope, s->name) != 0) 
    s = s->parent;

  while(s != NULL) {
    BucketList l = s->bucket[h];
    while(l != NULL && strcmp(name, l->name) != 0) 
      l = l->next;

    if(l == NULL) s = s->parent;
    else return l; 
  }
}

/* Procedure printSymTab prints a formatted 
 * listing of the symbol table contents 
 * to the listing file
 */

void printSymTab(FILE * listing)
{ int i;
  fprintf(listing, "SymbolTable : \n");
  fprintf(listing,"Variable Name       Type        Location       Scope      Line Numbers\n");
  fprintf(listing,"-------------  --------------  ----------  -------------  ------------\n");
  ScopeList s = symbolTable;
  while(s != NULL) {
    for(i=0;i<SIZE;++i) {
      if(s->bucket[i] != NULL) {
        BucketList l = s->bucket[i];
        while(l != NULL) {
          LineList t = l->lines;
          fprintf(listing,"%-14s ",l->name);
          switch(l->type) {
            case Void:
              fprintf(listing,"%-16s ","Void");
              break;
            case Integer:
              fprintf(listing,"%-16s ","Integer");
              break;
            case IntegerArray:
              fprintf(listing, "%-16s ","IntegerArray");
              break;
            default:
              break;
          }
          fprintf(listing,"%-8d  ",l->memloc);
          fprintf(listing,"%-14s ",s->name);
          while(t != NULL) {
            fprintf(listing,"%4d ",t->lineno);
            t = t->next;
          }
          fprintf(listing,"\n");
          l = l->next;
        }
      }
    }
    s = s->parent;
  }
} /* printSymTab */
