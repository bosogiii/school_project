#
# Makefile for TINY
# Gnu C Version
# K. Louden 2/3/98
#

CC = gcc

CFLAGS = 

OBJS_FLEX  = main.o util.o lex.yy.o parse.o symtab.o code.o

OBJS_FLEX_YACC = main.o util.o symtab.o code.o lex.yy.o y.tab.o


y.tab.h: cminus.y
	yacc -d -v cminus.y

cminus_flex_yacc: $(OBJS_FLEX_YACC)
	$(CC) $(CFLAGS) $(OBJS_FLEX_YACC) -o cminus_flex_yacc -lfl

lex.yy.o: cminus.l scan.h util.h globals.h
	flex cminus.l
	$(CC) $(CFLAGS) -c lex.yy.c

y.tab.o: globals.h util.h scan.h parse.h
	$(CC) $(CFLAGS) -c y.tab.c

main.o: main.c globals.h util.h scan.h parse.h analyze.h cgen.h
	$(CC) $(CFLAGS) -c main.c

util.o: util.c util.h globals.h
	$(CC) $(CFLAGS) -c util.c

scan.o: scan.c scan.h util.h globals.h
	$(CC) $(CFLAGS) -c scan.c

parse.o: parse.c parse.h scan.h globals.h util.h
	$(CC) $(CFLAGS) -c parse.c

symtab.o: symtab.c symtab.h
	$(CC) $(CFLAGS) -c symtab.c

analyze.o: analyze.c globals.h symtab.h analyze.h
	$(CC) $(CFLAGS) -c analyze.c

code.o: code.c code.h globals.h
	$(CC) $(CFLAGS) -c code.c

cgen.o: cgen.c globals.h symtab.h code.h cgen.h
	$(CC) $(CFLAGS) -c cgen.c

clean:
	-rm $(OBJS)
	-rm lex.yy.c
	-rm cminus_flex
	-rm $(OBJS_FLEX)
	-rm $(OBJS_FLEX_YACC)
	-rm cminus_flex_yacc
	-rm y.tab.c
	-rm y.tab.h
	-rm y.output

tm: tm.c
	$(CC) $(CFLAGS) tm.c -o tm

test:
	-./cminus_flex_yacc test.cm

all: y.tab.h cminus_flex_yacc

