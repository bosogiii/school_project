#ifndef _SYS_DESC_H_
#define _SYS_DESC_H_


#define TIMEOUT_PER_SECOND    50

#define KERNEL_CS			0x0008
#define KERNEL_DS			0x0010

#define TMR_TSS_SEG			0x0038
#define SOFT_TS_TSS_SEG		0x0040

#define SYSTEM_TMR_INT_NUMBER	0x20
#define SOFT_TASK_SW_INT_NUMBER	0x30

#pragma pack(push, 1)

typedef struct _IDT_GATE {
	WORD	offset_low;
	WORD	selector;
	WORD	type;
	WORD	offset_high;
}	IDT_GATE, *PIDT_GATE;

struct _DESC_TABLE_REG {
	WORD	size;
	int		address;
};

typedef struct _DESC_TABLE_REG	IDTR_DESC;
typedef struct _DESC_TABLE_REG	*PIDTR_DESC;
typedef struct _DESC_TABLE_REG	GDTR_DESC;
typedef struct _DESC_TABLE_REG	*PGDTR_DESC;
typedef struct _DESC_TABLE_REG	LDTR_DESC;
typedef struct _DESC_TABLE_REG	*PLDTR_DESC;

#pragma pack(pop)

#endif