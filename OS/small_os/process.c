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

//Process ����Ʈ�� �����ϴ� ����ü


typedef struct _PROCESS_MANAGER_BLOCK {
	DWORD								process_count;				//���� �ý��۳��� ��� process ��
	DWORD								next_process_id;			//process ����Ʈ ������ ���� process�� ���� process id
	struct _THREAD_CONTROL_BLOCK		*pt_current_thread;			//���� ����ǰ� �ִ� thread�� ���¸� ������ �ִ� ����ü ����
	struct _PROCESS_CONTROL_BLOCK		*pt_head_process;			//����Ʈ�� head�� ��ġ�ϰ� �ִ� process�� ���� ������
} PROCESS_MANAGER_BLOCK, *PPROCESS_MANAGER_BLOCK;

//�ý��ۿ��� �����ؾ��ϴ� Process�� Thread�� ����Ʈ�� ���� ������ �����ϴ� ����ü


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


static BOOL m_bShowTSWatchdogClock; //�ٶ����� ���
static DWORD m_TickCount;	//�ý����� ƽ ���� �����ϴ� ����


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

//Process ID ����
static DWORD PspGetNextProcessID(void)
{
	DWORD process_id;

ENTER_CRITICAL_SECTION();
	process_id = m_ProcMgrBlk.next_process_id++;
EXIT_CRITICAL_SECTION();

	return process_id;
}

//Thread ID ����
static DWORD PspGetNextThreadID(HANDLE ProcessHandle)
{
	///////////���� �ۼ��� �ּ���///////////////////////
}

//���ο� ���μ����� ���� ������ ã�Ƽ� ����
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

//���ο� �����带 ���� ������ ã�Ƽ� ����
static BOOL PspAddNewThread(HANDLE ProcessHandle, HANDLE ThreadHandle)
{
	///////////���� �ۼ��� �ּ���///////////////////////
}

//�ʱ� ���μ����� �������� ������ ����
static BOOL PspCreateSystemProcess(void)
{
	HANDLE process_handle;
	HANDLE init_thread_handle, idle_thread_handle, process_cutter_handle, thread_cutter_handle;
	HANDLE tmr_thread_handle, sw_task_sw_handle;

	//���� ���μ����� �������ִ� PSCreateProcess �Լ� ȣ��
	if(!PsCreateProcess(&precess_handle))
		return FALSE;

	//���μ����� �����ϱ� ���� ���̽��� �� ���� ������(init ������) ����
	if(!PsCreateThread(&init_thread_handle, process_handle, NULL, NULL, DEFAULT_STACK_SIZE, FALSE))
		return FALSE;

	//�ʱ� �������� �鸵ũ(Prev-Link)����
	HalSetupTaskLink(&PsGetThreadPtr(init_thread_handle)->thread_tss32, TASK_SW_SEG);

	//�ʱ� �������� TSS�� GDT���� ����
	HalWriteTssIntoGdt(&PsGEtThreadPtr(init_thread_handle)->thread_tss32, sizeof(TSS_32), INIT_TSS_SEG, FALSE);
	_asm{
		push	ax
		mov		ax, INIT_TSS_SEG
		ltr		ax
		pop		ax
	}

	return TRUE;
}

//���μ��� ���� �Լ� (PID�Ҵ� �� ����)
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

//������ ���� �Լ�
KERNELAPI BOOL PsCreateThread(OUT PHANDLE ThreadHandle, IN HANDLE ProcessHandle, IN PKSTART_ROUTINE StartRoutine, 
					 IN PVOID StartContext, IN DWORD StackSize, IN BOOL AutoDelete)
{
	PTHREAD_CONTROL_BLOCK  pThread;
	int *pStack;

	//�޸� �Ҵ�
	pThread = MmAllocateNonCachedMemory(sizeof(PROCESS_CONTROL_BLOCK));
	if(pThread == NULL) return FALSE;
	//�����忡�� ����� ���� �Ҵ�
	pStack = MmAllocatedNonChchedMemory(StackSize);
	if(pStack == NULL) return FALSE;

	//�θ� ���μ����� �ڵ� ����
	pThread->parent_proecess_handler		= ProcessHandler;
	//Thread id  �� handler �Ҵ�
	pThread->thread_id						= PspGetNextThreadID(ProcessHandler);
	pThread->thread_handle					= (HANDLE)pThread;
	pThread->thread_status					= THREAD_STATUS_STOP; //thread ���¸� stop���� ����
	pThread->auto_delete					= AutoDelete;
	pThread->pt_next_thread					= NULL;
	//�����尡 �����ؾ� �ϴ� �Լ�(StartRoutine), �Լ��� �Ѿ�� ����(StratContext), ���� ������ ����
	pThread->start_routine					= StartRoutine;
	pThread->start_context					= StartContext;
	pThread->pt_stack_base_address			= pStack;
	pThread->stack_size						= StackSize;
	//PspAddNewThread �Լ��� ���� Process�� ������ �����帣 �߰�
	if(!PspAddNewThread(ProcessHandler, (HANDLE)pThread)) return FALSE;

	HalSetupTSS(&pThread->thread_tss32, TRUE, (int)PspTaskEntryPoint, pStack, StackSize);

	*ThreadHandler = pThread;

	return TRUE;

}