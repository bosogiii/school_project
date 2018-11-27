#include "myoksos.h"

#define MEMORY_POOL_START_ADDRESS		0x00200000

#define MEM_BLK_SIZE		512
#define MEM_BLK_FREE		0
#define MEM_BLK_USED		1

typedef struct _MEM_BLK_DESC {
	DWORD		status;
	DWORD		block_size;
	struct _MEM_BLK_DESC	*pNext;
} MEM_BLK_DESC, *PMEM_BLK_DESC;

typedef struct _MEM_BLK_MANAGER {
	DWORD		nBlocks;
	DWORD		nUsedBlocks;
	DWORD		nFreeBlocks;
	MEM_BLK_DESC	*pDescEntry;
	int				*pPoolEntry;
} MEM_BLK_MANAGER, *PMEM_BLK_MANAGER;




static DWORD		m_MemSize;

static MEM_BLK_MANAGER	m_MemBlkManager;

static BOOL	MmpCheckMemorySize(void);
static BOOL MmpCreateMemPoolBlk(void);
static DWORD MmpGetRequiredBlocksFromBytes(DWORD bytes);


BOOL MmkInitializeMemoryManager(VOID)
{
	if(!MmpCheckMemorySize()) {
		DbgPrint("MmpCheckMemorySize() returned an error. \r\n");
		return FALSE;
	}

	if(!MmpCreateMemPoolBlk()){
		DbgPrint("MmpCreateMemPoolBlk() returned an error . \r\n");
		return FALSE;
	}
	DbgPrint("Memory Manager is initialized!!\r\n");

	return TRUE;
}
static BOOL	MmpCheckMemorySize(void)
{
	BOOL bResult;
	DWORD *pAddr = (DWORD *)0x00000000, tmp;

	while(1) {
		pAddr += (4*1024*1024);
		tmp = *pAddr;
		*pAddr = 0x11223344;
		if(*pAddr != 0x11223344)
			break;

		*pAddr = tmp;
	}

	ENTER_CRITICAL_SECTION();

	m_MemSize = (DWORD)pAddr;
	bResult = (m_MemSize < MEMORY_POOL_START_ADDRESS+(1*1024*1024) ? FALSE : TRUE);
	EXIT_CRITICAL_SECTION();

	return bResult;
}

static BOOL MmpCreateMemPoolBlk(void)
{
	DWORD dwUsableMemSize;
	DWORD dwBlksOfUsableMem;
	DWORD dwBlksOfAllocatableMem;
	DWORD dwBlksOfDescs;
	DWORD i;

	int *pPoolEntry;
	MEM_BLK_DESC *pPrev, *pCur;

ENTER_CRITICAL_SECTION();
	dwUsableMemSize = m_MemSize - MEMORY_POOL_START_ADDRESS;
EXIT_CRITICAL_SECTION();

	dwBlksOfUsableMem	= MmpGetRequiredBlocksFromBytes(dwUsableMemSize);
	dwBlksOfDescs		= MmpGetRequiredBlocksFromBytes(dwBlksOfUsableMem*sizeof(MEM_BLK_DESC));

	dwBlksOfAllocatableMem = dwBlksOfUsableMem-dwBlksOfDescs;

	dwBlksOfDescs	= MmpGetRequiredBlocksFromBytes(dwBlksOfAllocatableMem*sizeof(MEM_BLK_DESC));

	pPoolEntry	= (int*)(MEMORY_POOL_START_ADDRESS+dwBlksOfDescs*MEM_BLK_SIZE);

ENTER_CRITICAL_SECTION();
	m_MemBlkManager.nBlocks	= dwBlksOfAllocatableMem;
	m_MemBlkManager.nUsedBlocks = 0;
	m_MemBlkManager.nFreeBlocks = dwBlksOfAllocatableMem;
	m_MemBlkManager.pDescEntry = (MEM_BLK_DESC*)MEMORY_POOL_START_ADDRESS;
	m_MemBlkManager.pPoolEntry = pPoolEntry;

	pPrev = m_MemBlkManager.pDescEntry;
	pPrev->status=MEM_BLK_FREE;

	for(i=1; i<dwBlksOfAllocatableMem; i++)
	{
		pCur = (MEM_BLK_DESC*)(MEMORY_POOL_START_ADDRESS+sizeof(MEM_BLK_DESC)*i);
		pCur->status = MEM_BLK_FREE;
		pCur->block_size =0;
		pPrev->pNext = pCur;
		pPrev=pCur;
	}
	pCur->pNext = NULL;
EXIT_CRITICAL_SECTION();
	return TRUE;
}

static DWORD MmpGetRequiredBlocksFromBytes(DWORD bytes)
{
	DWORD dwBlocks = 0;

	dwBlocks = bytes/MEM_BLK_SIZE;
	if(bytes % MEM_BLK_SIZE)
		dwBlocks++;

	return dwBlocks;
}