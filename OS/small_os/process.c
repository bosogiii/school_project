#include "myoksos.h"
#include "sys_desc.h"


#define MAX_CUTTING_ITEM				30

typedef struct _THREAD_CONTROL_BLOCK {
	HANDLE								parent_process_handle;		/*memory address*/

	DWORD								thread_id;					/*thread id*/
	HANDLE								thread_handle;				/*momory address*/
	THREAD_STATUS						thread_status;				/*thread status*/
	BOOL								auto_delete;

	struct _THREAD_CONTROL_BLOCK		*pt_next_thread;

	PKSTART_ROUTINE						start_routine;				/*program entr point*/
	PVOID								start_context;				/*context to be passed into the entry routine*/
	int									*pt_stack_base_address;		/*stack vase address*/
	DWORD								stack_size;					/*stack size*/
	TSS_32								thread_tss32;				/*TSS32 BLOCK*/
} THREAD_CONTROL_BLOCK, *PTHREAD_CONTROL_BLOCK;


typedef struct _PROCESS_CONTROL_BLOCK {
	DWORD								process_id;					/*process id*/
	HANDLE								process_handle;				/*memory address*/

	struct _PROCESS_CONTROL_BLOCK		*pt_next_process;			/*next process point used by RR-Scheduler */

	DWORD								thread_count;				/*number of threads*/
	DWORD								next_thread_id;				/*next thread id used in this prosess*/
	struct _THREAD_CONTROL_BLOCK		*pt_head_thread;			/*first thread point*/
} PROCESS_CONTROL_BLOCK, *PPROCESS_CONTROL_BLOCK;

//Process 리스트를 관리하는 구조체


typedef struct _PROCESS_MANAGER_BLOCK {
	DWORD								process_count;				//현재 시스템내의 모든 process 수
	DWORD								next_process_id;			//process 리스트 내에서 현재 process의 다음 process id
	struct _THREAD_CONTROL_BLOCK		*pt_current_thread;			//현재 실행되고 있는 thread의 상태를 가지고 있는 구조체 변수
	struct _PROCESS_CONTROL_BLOCK		*pt_head_process;			//리스트의 head에 위치하고 있는 process에 대한 포인터
} PROCESS_MANAGER_BLOCK, *PPROCESS_MANAGER_BLOCK;

//시스템에서 제거해야하는 Process와 Thread의 리스트에 대한 정보를 관리하는 구조체


typedef struct _CUTTING_LIST {
	BYTE								count;
	BYTE								head;
	BYTE								tail;
	HANDLE								handle_list[MAX_CUTTING_ITEM];

} CUTTING_LIST, *PCUTTING_LIST;


static DWORD  PspGetNextProcessID(void);
static BOOL   PspAddNewProcess(HANDLE ProcessHandle);
static DWORD  PspGetNextThreadID(HANDLE ProcessHandle);
static BOOL   PspAddNewThread(HANDLE ProcessHandle, HANDLE ThreadHandle);

static BOOL PspCreateSystemProcess(void);


static PROCESS_MANAGER_BLOCK m_ProcMgrBlk;
static CUTTING_LIST m_ProcessCuttingList;
static CUTTING_LIST m_ThreadCuttingList;


static BOOL m_bShowTSWatchdogClock; //바람개비 모양
static DWORD m_TickCount;	//시스템의 틱 값을 저장하는 변수


BOOL PskInitializeProcessManager(VOID)
{
	m_ProcMgrBlk.process_count		= 0;
	m_ProcMgrBlk.next_process_id	= 0;
	m_ProcMgrBlk.pt_current_thread  = 0;
	m_ProcMgrBlk.pt_head_process	= NULL;

	m_ProcessCuttingList.count		= 0;
	m_ProcessCuttingList.head		= 0;
	m_ProcessCuttingList.tail		= 0;

	m_bShowTSWatchdogClock			= TRUE;
	m_TickCount						= 0;

	if(!PspCreateSystemProcess()){
			DbgPrint("PspCreateSystemProcess() returned an error.\r\n");
			return FALSE;
	}

	return TURE;
}

//Process ID 생성
static DWORD PspGetNextProcessID(void)
{
	DWORD process_id;

ENTER_CRITICAL_SECTION();
	process_id = m_ProcMgrBlk.next_process_id++;
EXIT_CRITICAL_SECTION();

	return process_id;
}

//Thread ID 생성
static DWORD PspGetNextThreadID(HANDLE ProcessHandle)
{
	///////////내용 작성해 주세요///////////////////////
}

//새로운 프로세스를 넣을 공간을 찾아서 생성
static BOOL PspAddNewProcess(HANDLE ProcessHandle)
{
	PPROCESS_CONTROL_LOCK *pt_next_process;

ENTER_CRITICAL_SECTION();
	pt_next_process = &m_ProcMgrBlk.pt_head_process;
	while(*pt_next_process)
		pt_next_process = &(*pt_next_process)->pt_enxt_process;
	*pt_next_process = PsGetProcessPtr(ProcessHandle);
	m_ProcMgrBlk.process_count++;
EXIT_CRITICAL_SECTION();

	return TURE;
}

//새로운 쓰레드를 넣을 공간을 찾아서 생성
static BOOL PspAddNewThread(HANDLE ProcessHandle, HANDLE ThreadHandle)
{
	///////////내용 작성해 주세요///////////////////////
}

//초기 프로세스와 쓰레드의 생성과 설정
static BOOL PspCreateSystemProcess(void)
{
	HANDLE process_handle;
	HANDLE init_thread_handle, idle_thread_handle, process_cutter_handle, thread_cutter_handle;
	HANDLE tmr_thread_handle, sw_task_sw_handle;

	//메인 프로세스를 생성해주는 PSCreateProcess 함수 호출
	if(!PsCreateProcess(&precess_handle))
		return FALSE;

	//프로세스를 생성하기 위해 베이스가 될 메인 쓰레드(init 쓰레드) 생성
	if(!PsCreateThread(&init_thread_handle, process_handle, NULL, NULL, DEFAULT_STACK_SIZE, FALSE))
		return FALSE;

	//초기 쓰레드의 백링크(Prev-Link)설정
	HalSetupTaskLink(&PsGetThreadPtr(init_thread_handle)->thread_tss32, TASK_SW_SEG);

	//초기 쓰레드의 TSS를 GDT내에 설정
	HalWriteTssIntoGdt(&PsGEtThreadPtr(init_thread_handle)->thread_tss32, sizeof(TSS_32), INIT_TSS_SEG, FALSE);
	_asm{
		push	ax
		mov		ax, INIT_TSS_SEG
		ltr		ax
		pop		ax
	}

	return TRUE;
}

//프로세스 생성 함수 (PID할당 등 관리)
KERNELAPI BOOL PsCreateProcess(OUT PHANDLE ProcessHandle)
{
	PPROCESS_CONTROL_BLOCK  pProcess;

	pProcess = MmAllocateNonCachedMemory(sizeof(PROCESS_CONTROL_BLOCK));
	if(pProcess == NULL) return FALSE;

	pProcess->process_id		= PspGetNextProcessID();
	pProcess->process_handle	= (HANDLE)pProcess;
	pProcess->pt_next_process	= NULL;
	pProcess->thread_count		= 0;
	pProcess->next_thread_id	= 0;
	pProcess->pt_head_thread	= NULL;
	if(!PspAddNewProcess((HANDLE)pProcess)) return FALSE;

	*ProcessHandle = pProcess;

	return TRUE;
}

//쓰레드 생성 함수
KERNELAPI BOOL PsCreateThread(OUT PHANDLE ThreadHandle, IN HANDLE ProcessHandle, IN PKSTART_ROUTINE StartRoutine, 
					 IN PVOID StartContext, IN DWORD StackSize, IN BOOL AutoDelete)
{
	PTHREAD_CONTROL_BLOCK  pThread;
	int *pStack;

	//메모리 할당
	pThread = MmAllocateNonCachedMemory(sizeof(PROCESS_CONTROL_BLOCK));
	if(pThread == NULL) return FALSE;
	//쓰레드에서 사용할 스택 할당
	pStack = MmAllocatedNonChchedMemory(StackSize);
	if(pStack == NULL) return FALSE;

	//부모 프로세스의 핸들 설정
	pThread->parent_proecess_handler		= ProcessHandler;
	//Thread id  및 handler 할당
	pThread->thread_id						= PspGetNextThreadID(ProcessHandler);
	pThread->thread_handle					= (HANDLE)pThread;
	pThread->thread_status					= THREAD_STATUS_STOP; //thread 상태를 stop으로 설정
	pThread->auto_delete					= AutoDelete;
	pThread->pt_next_thread					= NULL;
	//쓰레드가 실행해야 하는 함수(StartRoutine), 함수에 넘어가는 인자(StratContext), 스택 사이즈 설정
	pThread->start_routine					= StartRoutine;
	pThread->start_context					= StartContext;
	pThread->pt_stack_base_address			= pStack;
	pThread->stack_size						= StackSize;
	//PspAddNewThread 함수를 통해 Process에 생성된 쓰레드르 추가
	if(!PspAddNewThread(ProcessHandler, (HANDLE)pThread)) return FALSE;

	HalSetupTSS(&pThread->thread_tss32, TRUE, (int)PspTaskEntryPoint, pStack, StackSize);

	*ThreadHandler = pThread;

	return TRUE;

}