#include "myoksos.h"

BOOL KrnInitializeKernel(VOID);

extern BOOL HalInitializeHal(VOID);


BOOL KrnInitializeKernel(VOID)
{
	if(!HalInitializeHal()){
		DbgPrint("HalInitializeHal() returned an error.\r\n");
		return FALSE;
	}

	//메모리 초기화 호출
	if(!MmkInitializeMemoryManager()) {
		DbgPrint("MmkInitializeMemoryManager() returned an error .\r\n");
		return FALSE;
	}

	//프로세스 초기화 함수 호출
	if(!PskInitializeProcessManager()){
		DbgPrint("PskInitializeProcessManager() returned an error.\r\n");
		return FALSE;
	}
	
	return TRUE;
}
