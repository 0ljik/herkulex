import serial
from time import sleep

class herkulex:
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

    def __init__(self, port, baud):
        super(herkulex, self).__init__()
        self.ser = serial.Serial(port=port[0], baudrate=baud)
        self.baud = baud
        #self.ser = appserial
        self._pSize = 0x00
        self._pID = 0x00
        self._cmd = 0x00
        self._lengthString = 0
        self._ck1 = 0x00
        self._ck2 = 0x00

        self._conta = 0

        self._XOR = 0x00
        self._playTime = 0x00
        self.__data=bytearray(self.__DATA_SIZE)
        self.__dataEx=bytearray(self.__DATA_MOVE+8)
        self.__moveData=bytearray(self.__DATA_MOVE)

    def initialize(self):
        try:
            self._conta=0
            self._lengthString=0
            print('lenset')
            sleep(0.1)
            print('sleep')
            self.clearError(self.__BROADCAST_ID)
            print('errclear')
            sleep(0.01)
            self.ACK(1)
            slep(0.01)
            self.torqueON(self.__BROADCAST_ID)
            print('torqon')
            sleep(0.01)
        except Exception as e:
            print('e'+e
            )


    def torqueON(self, servoID):
    	self._pSize = 0x0A               # 3.Packet size 7-58
    	self._pID   = servoID            # 4. Servo ID
    	self._cmd   = self.__HRAMWRITE          # 5. CMD
    	self.__data[0]=0x34               # 8. Address
    	self.__data[1]=0x01               # 9. Length
    	self.__data[2]=0x60               # 10. 0x60=Torque ON
    	self._lengthString=3             # lenghtData

    	self._ck1=self.checksum1()	#6. Checksum1
    	self._ck2=self.checksum2()					#7. Checksum2
    	print('torqon')
    	self.__dataEx[0] = 0xFF			# Packet Header
    	self.__dataEx[1] = 0xFF			# Packet Header
    	self.__dataEx[2] = self._pSize	 		# Packet Size
    	self.__dataEx[3] = self._pID			# Servo ID
    	self.__dataEx[4] = self._cmd			# Command Ram Write
    	self.__dataEx[5] = self._ck1			# Checksum 1
    	self.__dataEx[6] = self._ck2			# Checksum 2
    	self.__dataEx[7] = self.__data[0] 		# Address 52
    	self.__dataEx[8] = self.__data[1] 		# Length
    	self.__dataEx[9] = self.__data[2] 		# Torque ON
    	print('datasending')
    	self.sendData()
    	print('datasentding')

    def torqueOFF(self, servoID):
    	self._pSize = 0x0A               # 3.Packet size 7-58
    	self._pID   = servoID            # 4. Servo ID
    	self._cmd   = self.__HRAMWRITE          # 5. CMD
    	self.__data[0]=0x34               # 8. Address
    	self.__data[1]=0x01               # 9. Lenght
    	self.__data[2]=0x00               # 10. 0x00=Torque Free
    	self._lengthString=3             # lenghtData
    	self._ck1=self.checksum1()	#6. Checksum1
    	self._ck2=self.checksum2()					#7. Checksum2
    	self.__dataEx[0] = 0xFF			# Packet Header
    	self.__dataEx[1] = 0xFF			# Packet Header
    	self.__dataEx[2] = self._pSize	 		# Packet Size
    	self.__dataEx[3] = self._pID			# Servo ID
    	self.__dataEx[4] = self._cmd			# Command Ram Write
    	self.__dataEx[5] = self._ck1			# Checksum 1
    	self.__dataEx[6] = self._ck2			# Checksum 2
    	self.__dataEx[7] = self.__data[0] 		# Address 52
    	self.__dataEx[8] = self.__data[1] 		# Length
    	self.__dataEx[9] = self.__data[2]       #length
        #print(self.__dataEx)
    	self.sendData()
    def ACK(self, valueACK):
    	self._pSize = 0x0A               # 3.Packet size 7-58
    	self._pID   = 0xFE	            # 4. Servo ID
    	self._cmd   = self.__HRAMWRITE          # 5. CMD
    	self.__data[0]=0x34               # 8. Address
    	self.__data[1]=0x01               # 9. length
    	self.__data[2]=valueACK           # 10.Value. 0=No Replay, 1=Only reply to READ CMD, 2=Always reply
    	self._lengthString=3             # lengthData

    	self._ck1=self.checksum1()	#6. Checksum1
    	self._ck2=self.checksum2()					#7. Checksum2

    	self.__dataEx[0] = 0xFF			# Packet Header
    	self.__dataEx[1] = 0xFF			# Packet Header
    	self.__dataEx[2] = self._pSize	 		# Packet Size
    	self.__dataEx[3] = self._pID			# Servo ID
    	self.__dataEx[4] = self._cmd			# Command Ram Write
    	self.__dataEx[5] = self._ck1			# Checksum 1
    	self.__dataEx[6] = self._ck2			# Checksum 2
    	self.__dataEx[7] = self.__data[0] 		# Address 52
    	self.__dataEx[8] = self.__data[1] 		# Length
    	self.__dataEx[9] = self.__data[2] 		# Value
    	self.sendData()

    def clearError(self, servoID):
    	self._pSize = 0x0B               # 3.Packet size 7-58
    	self._pID   = servoID     		# 4. Servo ID - 253=all servos
    	self._cmd   = self.__HRAMWRITE          # 5. CMD
    	self.__data[0]=0x30               # 8. Address
    	self.__data[1]=0x02               # 9. length
    	self.__data[2]=0x00               # 10. Write error=0
    	self.__data[3]=0x00               # 10. Write detail error=0

    	self._lengthString=4             # lengthData

    	self._ck1=self.checksum1()	#6. Checksum1
    	self._ck2=self.checksum2()					#7. Checksum2

    	self.__dataEx[0] = 0xFF			# Packet Header
    	self.__dataEx[1] = 0xFF			# Packet Header
    	self.__dataEx[2] = self._pSize	 		# Packet Size
    	self.__dataEx[3] = self._pID			# Servo ID
    	self.__dataEx[4] = self._cmd			# Command Ram Write
    	self.__dataEx[5] = self._ck1			# Checksum 1
    	self.__dataEx[6] = self._ck2			# Checksum 2
    	self.__dataEx[7] = self.__data[0] 		# Address 52
    	self.__dataEx[8] = self.__data[1] 		# Length
    	self.__dataEx[9] = self.__data[2] 		# Value1
    	self.__dataEx[10]= self.__data[3] 		# Value2
    	self.sendData()

    def setLed(servoID, valueLed):
    	self._pSize   = 0x0A               # 3.Packet size 7-58
    	self._pID     = self.servoID            # 4. Servo ID
    	self._cmd     = self.__HRAMWRITE          # 5. CMD
    	self.__data[0] = 0x35               # 8. Address 53
    	self.__data[1] = 0x01               # 9. Lenght
    	self.__data[2] = valueLed           # 10.LedValue
    	self._lenghtString=3               # lenghtData

    	self._ck1=checksum1()	#6. Checksum1
    	self._ck2=checksum2()					#7. Checksum2

    	self.__dataEx[0] = 0xFF			# Packet Header
    	self.__dataEx[1] = 0xFF			# Packet Header
    	self.__dataEx[2] = self._pSize	 		# Packet Size
    	self.__dataEx[3] = self._pID			# Servo ID
    	self.__dataEx[4] = self._cmd			# Command Ram Write
    	self.__dataEx[5] = self._ck1			# Checksum 1
    	self.__dataEx[6] = self._ck2			# Checksum 2
    	self.__dataEx[7] = self.__data[0]        # Address
    	self.__dataEx[8] = self.__data[1]       	# Length
    	self.__dataEx[9] = self.__data[2]        # Value

    	sendData()
    def checksum1(self):
        self._XOR = 0
        self._XOR = self._XOR ^ self._pSize
        self._XOR = self._XOR ^ self._pID
        self._XOR = self._XOR ^ self._cmd
        for i in range(self._lengthString):
            self._XOR = self._XOR ^ self.__data[i]
        return self._XOR&0xFE

    def checksum2(self):
      return (~self._XOR)&0xFE

    def sendData(self):
        print('buffclin')
        #self.ser.read()
        self.clearBuffer() 		#clear the serialport buffer - try to do it!
        print('buffcld')
        self.ser.write(self.__dataEx)
        sleep(0.001)

    def readData(self, size):
        self.__dataEx = self.ser.read(size)

        """
        while((self.ser.inWaiting() < size) & (Time_Counter < TIME_OUT)){
        		Time_Counter++;
        		sleep(0.0001);  //wait 1 millisecond for 10 times
		}

		while (ser.inWaiting() > 0){
			inchar = (byte)SwSerial.read();
			if ( (inchar == 0xFF) & ((byte)SwSerial.peek() == 0xFF) ){
					beginsave=1;
					i=0; 				 # if found new header, begin again
			}
			if (beginsave==1 && i<size) {
				   dataEx[i] = inchar;
				   i++;
			}
		}
		SwSerial.flush()"""


    def clearBuffer(self):
    	self.ser.reset_input_buffer()
    	sleep(0.002)

"""@classmethod
    def connect(cls, id):
        self.ser=appserial.connect(port,baud)
        return cls(id, id)

    @classmethod
    def getid(self.__BROADCAST_ID):
        return self.__BROADCAST_ID

    @staticmethod
    def connect(self.__BROADCAST_ID):
        return self.__BROADCAST_ID
            @classmethod
            def getid(cls, self.__BROADCAST_ID):
                appserial.send()
                input=appserial.read()
                return cls()"""
