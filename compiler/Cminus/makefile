#
# Makefile for TINY
# Gnu C Version
# K. Louden 2/3/98
#

CC = gcc

CFLAGS = -Wall -w -g

OBJS = y.tab.o main.o util.o lex.yy.o symtab.o code.o analyze.o


cminus: $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o cminus -lfl

lex.yy.o: cminus.l scan.h util.h globals.h
	flex cminus.l
	$(CC) $(CFLAGS) -c lex.yy.c

y.tab.o: cminus.y globals.h util.h scan.h parse.h
	yacc -d -v cminus.y
	$(CC) $(CFLAGS) -c y.tab.c

main.o: main.c globals.h util.h scan.h parse.h analyze.h cgen.h
	$(CC) $(CFLAGS) -c main.c

util.o: util.c util.h globals.h
	$(CC) $(CFLAGS) -c util.c

scan.o: scan.c scan.h util.h globals.h
	$(CC) $(CFLAGS) -c scan.c

parse.o: parse.c parse.h scan.h globals.h util.h
	$(CC) $(CFLAGS) -c parse.c

symtab.o: symtab.c globals.h symtab.h
	$(CC) $(CFLAGS) -c symtab.c

analyze.o: analyze.c globals.h symtab.h analyze.h
	$(CC) $(CFLAGS) -c analyze.c

code.o: code.c code.h globals.h
	$(CC) $(CFLAGS) -c code.c

cgen.o: cgen.c globals.h symtab.h code.h cgen.h
	$(CC) $(CFLAGS) -c cgen.c

clean:
	-rm lex.yy.c
	-rm cminus
	-rm $(OBJS)
	-rm y.tab.c
	-rm y.tab.h
	-rm y.output

tm: tm.c
	$(CC) $(CFLAGS) tm.c -o tm

test:
	-./cminus test.cm


