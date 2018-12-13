//CPU 클럭 설정
#define F_CPU 16000000

//ATmega128의 레지스터 등이 정의되어 있음
#include <avr/io.h>
//interrupt를 사용하는 데 필요한 정보들이 정의되어 있음
#include <avr/interrupt.h>
//_delay_ms 등 딜레이 함수가 정의되어 있음
#include <util/delay.h>

//herkulex 라이브러리의 헤더 파일을 포함
#include <herkulex.h>
//#include <USART0.h>
#include <TIMER0.h>

//DRS-0101의 Calibrated Position 정보를 사용하기 위한 구조체
typedef struct DrsCaliPos
{
	int				iPosition : 13;
	unsigned int	uiGPIO1 : 1;
	unsigned int	uiGPIO2 : 1;
	unsigned int	reserved : 1;
}DrsCaliPos;

//Calibrated Position 정보를 쉽게 다루기 위한 공용체
typedef union DrsUnionCaliPos
{
	DrsCaliPos		stCaliPos;
	unsigned int	uiCaliPos;
}DrsUnionCaliPos;

int main(void)
{
	//보낼 패킷과 받을 패킷이 저장될 패킷 구조체 선언
	DrsPacket stSendPacket, stRcvPacket;
	//Calibrated Position을 저장할 공용체 변수 선언
	DrsUnionCaliPos unCaliPos;
	//사용할 변수들 선언
	unsigned char ucResult;
	int iPos = 400;
	
	//포트 C의 입출력 방향 설정
	DDRC = 0b01111111;
	//포트 C의 출력 값 설정
	PORTC = 0b01111111;
	
	//전체 인터럽트를 비활성화
	cli();
	
	//HerkuleX를 사용하기 위해 초기화
	hklx_Init(115200);
	
	//전체 인터럽트를 활성화
	sei();
	
	//Torque Control에 0x60을 써서 토크를 거는 패킷 구성
	stSendPacket.ucPacketSize = MIN_PACKET_SIZE + 3;
	stSendPacket.ucChipID = 253;
	stSendPacket.ucCmd = CMD_RAM_WRITE;
	stSendPacket.unData.stRWData.ucAddress = 52;
	stSendPacket.unData.stRWData.ucLen = 1;
	stSendPacket.unData.stRWData.ucData[0] = 0x60;
	
	//패킷 보내기
	hklx_SendPacket(stSendPacket);
	
	while(1)
	{
		//목표 위치 변수 값 변경
		if(iPos == 400){
			iPos = 624;
		}			
		else{
			iPos = 400;
		}			
		
		//DRS-0101을 움직일 I_JOG 패킷 구성
		stSendPacket.ucPacketSize = MIN_PACKET_SIZE + CMD_I_JOG_STRUCT_SIZE;
		stSendPacket.ucChipID = BROADCAST_ID;
		stSendPacket.ucCmd = CMD_I_JOG;
		stSendPacket.unData.stIJogData.stIJog[0].stJog.uiValue = iPos;
		stSendPacket.unData.stIJogData.stIJog[0].stSet.ucStopFlag = 0;
		stSendPacket.unData.stIJogData.stIJog[0].stSet.ucMode = 0;
		stSendPacket.unData.stIJogData.stIJog[0].stSet.ucLedGreen = 1;
		stSendPacket.unData.stIJogData.stIJog[0].stSet.ucLedBlue = 1;
		stSendPacket.unData.stIJogData.stIJog[0].stSet.ucLedRed = 1;
		stSendPacket.unData.stIJogData.stIJog[0].stSet.ucJogInvalid = 0;
		stSendPacket.unData.stIJogData.stIJog[0].ucId = 253;
		stSendPacket.unData.stIJogData.stIJog[0].ucPlayTime = 50;
		
		//패킷 보내기
		hklx_SendPacket(stSendPacket);
	
		//다 움직일 때 까지 1초 대기
		_delay_ms(1000);
		
		//Calibrated Position을 읽어올 RAM_READ 패킷 구성
		stSendPacket.ucPacketSize = MIN_PACKET_SIZE + 2;
		stSendPacket.ucChipID = 253;
		stSendPacket.ucCmd = CMD_RAM_READ;
		stSendPacket.unData.stRWData.ucAddress = 58;
		stSendPacket.unData.stRWData.ucLen = 2;
		
		//패킷 보내기
		hklx_SendPacket(stSendPacket);
		
		//TIMEOUT 까지 기다릴 시간 설정. 2*15 = 30(ms)
		gucTimerTick=15;
		while(1){
			//패킷을 받는 함수를 호출해 결과를 ucResult에 저장
			ucResult = hklx_ucReceivePacket(&stRcvPacket);
			//결과 값이 DRS_RXWAITING이 아니면 빠져나옴
			if(ucResult != DRS_RXWAITING){
				break;
			}
			//30ms가 지나서 gucTimerTick이 0이 되면 빠져나옴
			if(gucTimerTick==0){
				ucResult = DRS_RXTIMEOUT;
				break;
			}				
		}
		
		//패킷 수신이 정상적으로 완료 시
		if(ucResult == DRS_RXCOMPLETE){
			//받은 데이터 2바이트를 공용체 변수에 저장
			unCaliPos.uiCaliPos = stRcvPacket.unData.stRWData.ucData[0] | 
								 (stRcvPacket.unData.stRWData.ucData[1]<<8);
			
			//목표 위치와 5 이내로 근접했으면 LED 모두 끔
			if((iPos - unCaliPos.stCaliPos.iPosition) > -5 && 
			   (iPos - unCaliPos.stCaliPos.iPosition) < 5){
				PORTC = 0b01111111;	
			}
			//목표 위치의 5 밖으로 나갔으면 LED 모두 켬
			else{
				PORTC = 0b00000000;
			}				
		}
		//패킷 수신이 정상적으로 이루어지지 않았을 때 LED 모두 켬
		else{
			PORTC = 0b00000000;
		}			
	}
	
	//함수의 형태에 맞게 정수값 반환
	return 1;
}