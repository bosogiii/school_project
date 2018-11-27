#include "myoksos.h"

static void halt(char *pMsg);

extern BOOL CrtInitializeDriver(VOID);


int myoksos_init(void)
{
	  //�ܼ� �ý��� �ʱ�ȭ �Լ� ȣ��
   if(!CrtInitializeDriver())
   {
      halt(NULL);
   }

   //Ŀ�� �ʱ�ȭ ��ƾ�� ȣ��
   if(!KrnInitializeKernel())
   {
	   halt("KrnInitializeKernel() returned an error.\r\n");
   }

   //���� �ʱ�ȭ ���н�, �� �κ� ���� (��ü �ý��� ����)
   halt("Booting Error!\r\n");
   return 0;
}

//Ŀ�� ���� �Լ�, ����� ����� ���� �޼��� ǥ��.
static void halt(char *pMsg)
{
   if(pMsg !=NULL){
      DbgPrint(pMsg);
      DbgPrint("Halting system.\r\n");
   }
   while(1);

}
