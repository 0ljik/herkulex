#ifndef TIMER0_H_
#define TIMER0_H_

#ifdef __TIMER0_C
	#define TIMER0_EXT
#else
	#define TIMER0_EXT extern
#endif

//타이머를 사용해 시간을 측정할 때의 전역변수
TIMER0_EXT volatile unsigned char gucTimerTick;
//타이머/카운터0의 초기화 함수
TIMER0_EXT void TIMER0_Init(void);

#endif /* TIMER0_H_ */