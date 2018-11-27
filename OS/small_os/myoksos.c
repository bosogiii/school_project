#include "myoksos.h"

static void halt(char *pMsg);

extern BOOL CrtInitializeDriver(VOID);


int myoksos_init(void)
{
	  //콘솔 시스템 초기화 함수 호출
   if(!CrtInitializeDriver())
   {
      halt(NULL);
   }

   //커널 초기화 루틴의 호출
   if(!KrnInitializeKernel())
   {
	   halt("KrnInitializeKernel() returned an error.\r\n");
   }

   //만약 초기화 실패시, 이 부분 실행 (전체 시스템 정지)
   halt("Booting Error!\r\n");
   return 0;
}

//커널 정지 함수, 디버그 모드일 때는 메세지 표시.
static void halt(char *pMsg)
{
   if(pMsg !=NULL){
      DbgPrint(pMsg);
      DbgPrint("Halting system.\r\n");
   }
   while(1);

}
