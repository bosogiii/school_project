#ifndef _MYOKSOS_H_
#define _MYOKSOS_H_

#include "types.h"
#include "debug.h"

#include "string.h"
#include "vsprintf.h"

#include "6845crt.h"


#define ENTER_CRITICAL_SECTION()     __asm  PUSHFD  __asm CLI

#define EXIT_CRITICAL_SECTION()      __asm  POPFD

extern KERNELAPI VOID WRITE_PORT_UCHAR(IN PUCHAR Port, IN UCHAR Value);

#endif
