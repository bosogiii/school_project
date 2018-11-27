#include "myoksos.h"

BOOL KrnInitializeKernel(VOID);

extern BOOL HalInitializeHal(VOID);


BOOL KrnInitializeKernel(VOID)
{
	if(!HalInitializeHal()){
		DbgPrint("HalInitializeHal() returned an error.\r\n");
		return FALSE;
	}

	//�޸� �ʱ�ȭ ȣ��
	if(!MmkInitializeMemoryManager()) {
		DbgPrint("MmkInitializeMemoryManager() returned an error .\r\n");
		return FALSE;
	}

	//���μ��� �ʱ�ȭ �Լ� ȣ��
	if(!PskInitializeProcessManager()){
		DbgPrint("PskInitializeProcessManager() returned an error.\r\n");
		return FALSE;
	}
	
	return TRUE;
}
