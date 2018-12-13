import appserial
from time import sleep

class herkulex(object):
    """docstring for herkulex."""
    def __init__(self, port, baud):
        super(herkulex, self).__init__()
        self.port = port
        self.baud = baud
        __DATA_SIZE=30		# buffer for input data
        __DATA_MOVE=50		# max 10 servos <---- change this for more servos!
        __TIME_OUT=5   	#timeout serial communication

        # SERVO HERKULEX COMMAND - See Manual p40
        __HEEPWRITE=0x01 	#Rom write
        __HEEPREAD=0x02 	#Rom read
        __HRAMWRITE=0x03 	#Ram write
        __HRAMREAD=0x04 	#Ram read
        __HIJOG=0x05 	#Write n servo with different timing
        __HSJOG=0x06 	#Write n servo with same time
        __HSTAT=0x07 	#Read error
        __HROLLBACK=0x08 	#Back to factory value
        __HREBOOT=0x09 	#Reboot

        # HERKULEX LED - See Manual p29
        __LED_GREEN =	 0x01
        __LED_BLUE  =   0x02
        __LED_CYAN  =   0x03
        __LED_RED   = 	 0x04
        __LED_GREEN2= 	 0x05
        __LED_PINK  =   0x06
        __LED_WHITE =   0x07

        # HERKULEX STATUS ERROR - See Manual p39
        __H_STATUS_OK					= 0x00
        __H_ERROR_INPUT_VOLTAGE 		= 0x01
        __H_ERROR_POS_LIMIT			= 0x02
        __H_ERROR_TEMPERATURE_LIMIT	= 0x04
        __H_ERROR_INVALID_PKT			= 0x08
        __H_ERROR_OVERLOAD			= 0x10
        __H_ERROR_DRIVER_FAULT  		= 0x20
        __H_ERROR_EEPREG_DISTORT		= 0x40

        # HERKULEX Broadcast Servo ID
        __BROADCAST_ID = 0xFE


        _pSize = 0
        _pID = 0
        _cmd = 0
        _lengthString = 0
        _ck1 = 0

        _conta = 0

        _XOR = 0
        _playTime = 0
        __data=bytearray(self.__DATA_SIZE)
        __dataEx=bytearray(self.__DATA_MOVE+8)
        __moveData=bytearray(self.__DATA_MOVE)

    @classmethod
    def connect(cls, id):
        self.ser=appserial.connect(port,baud)
        return cls(id, id)

    """@staticmethod
    def getid(brd_id):
        return brd_id"""

    def initialize():
        conta=0
        lenghtString=0
        sleep(0.1)
        clearError(brd_id)
        sleep(0.01)
        ACK(1)
        slep(0.01)
        torqueON(brd_id)
        sleep(0.01)

    @classmethod
    def getid(cls, brd_id):
        appserial.send()
        input=appserial.read()
        return cls()

    def ACK(int valueACK):
    	pSize = 0x0A               # 3.Packet size 7-58
    	pID   = 0xFE	            # 4. Servo ID
    	cmd   = HRAMWRITE          # 5. CMD
    	data[0]=0x34               # 8. Address
    	data[1]=0x01               # 9. Lenght
    	data[2]=valueACK           # 10.Value. 0=No Replay, 1=Only reply to READ CMD, 2=Always reply
    	lenghtString=3             # lenghtData

    	ck1=checksum1(data,lenghtString)	#6. Checksum1
    	ck2=checksum2(ck1)					#7. Checksum2

    	dataEx[0] = 0xFF			# Packet Header
    	dataEx[1] = 0xFF			# Packet Header
    	dataEx[2] = pSize	 		# Packet Size
    	dataEx[3] = pID			# Servo ID
    	dataEx[4] = cmd			# Command Ram Write
    	dataEx[5] = ck1			# Checksum 1
    	dataEx[6] = ck2			# Checksum 2
    	dataEx[7] = data[0] 		# Address 52
    	dataEx[8] = data[1] 		# Length
    	dataEx[9] = data[2] 		# Value

     	sendData(dataEx, pSize)

    def clearError(int servoID):
    	pSize = 0x0B               # 3.Packet size 7-58
    	pID   = servoID     		# 4. Servo ID - 253=all servos
    	cmd   = HRAMWRITE          # 5. CMD
    	data[0]=0x30               # 8. Address
    	data[1]=0x02               # 9. Lenght
    	data[2]=0x00               # 10. Write error=0
    	data[3]=0x00               # 10. Write detail error=0

    	lenghtString=4             # lenghtData

    	ck1=checksum1(data,lenghtString)	#6. Checksum1
    	ck2=checksum2(ck1)					#7. Checksum2

    	dataEx[0] = 0xFF			# Packet Header
    	dataEx[1] = 0xFF			# Packet Header
    	dataEx[2] = pSize	 		# Packet Size
    	dataEx[3] = pID			# Servo ID
    	dataEx[4] = cmd			# Command Ram Write
    	dataEx[5] = ck1			# Checksum 1
    	dataEx[6] = ck2			# Checksum 2
    	dataEx[7] = data[0] 		# Address 52
    	dataEx[8] = data[1] 		# Length
    	dataEx[9] = data[2] 		# Value1
    	dataEx[10]= data[3] 		# Value2

    	sendData(dataEx, pSize)


    def checksum1(byte* data, int lenghtString):
        XOR = 0
        XOR = XOR ^ pSize
        XOR = XOR ^ pID
        XOR = XOR ^ cmd
        for i in range(lenghtString):
            XOR = XOR ^ data[i]
        return XOR&0xFE

    def checksum2(int XOR):
      return (~XOR)&0xFE

    def sendData(byte* buffer, int lenght):
        clearBuffer() 		#clear the serialport buffer - try to do it!
        Serial1.write(buffer, lenght)
        sleep(0.001)

    def clearBuffer()
		Serial1.flush();
		while (Serial1.available()){
		Serial1.read();
		delayMicroseconds(200);
