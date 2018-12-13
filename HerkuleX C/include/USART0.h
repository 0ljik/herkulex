#ifndef USART0_H_
#define USART0_H_

//수신 버퍼의 사이즈 선언
#define USART_BUF_SIZE 256

#ifdef __USART0_C
	#define USART0_EXT
#else
	#define USART0_EXT extern
#endif

//수신 버퍼, 읽기 인덱스, 쓰기 인덱스, 데이터 수를 저장할 변수 선언
USART0_EXT volatile unsigned char gucRxBuffer[USART_BUF_SIZE];
USART0_EXT volatile unsigned char gucRxBufferReadIdx;
USART0_EXT volatile unsigned char gucRxBufferWriteIdx;
USART0_EXT volatile unsigned char gucRxBufferCnt;

//USART0의 초기화 함수
USART0_EXT void USART0_Init(unsigned long ulBaudRate);
//USART0로 문자 하나를 전송하는 함수
USART0_EXT void USART0_PutChar(unsigned char ucData);
//USART0로 문자 여러 개를 전송하는 함수
USART0_EXT void USART0_PutNChar(unsigned char *pucData, unsigned char ucCnt);
//USART0의 수신 버퍼에서 여러 개의 데이터를 읽어오는 함수
USART0_EXT unsigned char USART0_ucGetNChar(unsigned char *pucTarget, unsigned char ucCnt);
//USART0의 수신 버퍼에서 여러 개의 데이터를 버리는 함수
USART0_EXT unsigned char USART0_ucTrashNChar(unsigned char ucCnt);
//USART0의 수신 버퍼를 초기화하는 함수
USART0_EXT void USART0_ClearBuffer(void);

#endif /* USART0_H_ */