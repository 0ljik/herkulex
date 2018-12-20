import serial
from time import sleep


class herkulex:
    __DATA_SIZE = 30		# buffer for input data
    __DATA_MOVE = 50		# max 10 servos <---- change this for more servos!
    __TIME_OUT = 5  # timeout serial communication
    # SERVO HERKULEX COMMAND - See Manual p40
    __HEEPWRITE = 0x01  # Rom write
    __HEEPREAD = 0x02  # Rom read
    __HRAMWRITE = 0x03  # Ram write
    __HRAMREAD = 0x04  # Ram read
    __HIJOG = 0x05  # Write n servo with different timing
    __HSJOG = 0x06  # Write n servo with same time
    __HSTAT = 0x07  # Read error
    __HROLLBACK = 0x08  # Back to factory value
    __HREBOOT = 0x09  # Reboot

    # HERKULEX LED - See Manual p29
    __LED_GREEN = 0x01
    __LED_BLUE = 0x02
    __LED_CYAN = 0x03
    __LED_RED = 0x04
    __LED_GREEN2 = 0x05
    __LED_PINK = 0x06
    __LED_WHITE = 0x07
    __ledset = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]

    # HERKULEX STATUS ERROR - See Manual p39
    __H_STATUS_OK = 0x00
    __H_ERROR_INPUT_VOLTAGE = 0x01
    __H_ERROR_POS_LIMIT = 0x02
    __H_ERROR_TEMPERATURE_LIMIT = 0x04
    __H_ERROR_INVALID_PKT = 0x08
    __H_ERROR_OVERLOAD = 0x10
    __H_ERROR_DRIVER_FAULT = 0x20
    __H_ERROR_EEPREG_DISTORT = 0x40

    # HERKULEX Broadcast Servo ID
    __BROADCAST_ID = 0xFE

    def __init__(self, port, baud):
        super(herkulex, self).__init__()
        self.__ser = serial.Serial(port=port[0], baudrate=baud)
        # self.__baud = baud
        # self.__ser = appserial
        self.__pSize = 0x00
        self.__pID = 0x00
        self.__cmd = 0x00
        self.__lengthString = 0
        self.__ck1 = 0x00
        self.__ck2 = 0x00

        self.__conta = 0

        self.__XOR = 0x00
        self.__playTime = 0x00
        self.__data = bytearray(self.__DATA_SIZE)
        self.__dataEx = bytearray(self.__DATA_MOVE + 8)
        self.__moveData = bytearray(self.__DATA_MOVE)

    #  initialize servos
    def initialize(self):
        try:
            self.__conta = 0
            self.__lengthString = 0
            sleep(0.1)
            self.__clearError(self.__BROADCAST_ID)
            sleep(0.01)
            self.__ACK(1)
            sleep(0.01)
            self.__torqueON(self.__BROADCAST_ID)
            sleep(0.01)
        except Exception as e:
            print('e' + e)

    #  stat
    def stat(self, servoID):
        self.__pSize = 0x07  # 3.Packet size
        self.__pID = servoID  # 4.Servo ID - 0XFE=All servos
        self.__cmd = self.__HSTAT  # 5.CMD

        self.__ck1 = (self.__pSize ^ self.__pID ^ self.__cmd) & 0xFE
        self.__ck2 = (~(self.__pSize ^ self.__pID ^ self.__cmd)) & 0xFE

        self.__dataEx[0] = 0xFF			# Packet Header
        self.__dataEx[1] = 0xFF			# Packet Header
        self.__dataEx[2] = self.__pSize	 		# Packet Size
        self.__dataEx[3] = self.__pID			# Servo ID
        self.__dataEx[4] = self.__cmd			# Command Ram Write
        self.__dataEx[5] = self.__ck1			# Checksum 1
        self.__dataEx[6] = self.__ck2			# Checksum 2

        self.__sendData()
        sleep(0.002)
        self.__readData(9) 				# read 9 bytes from serial

        self.__pSize = self.__dataEx[2]           # 3.Packet size 7-58
        self.__pID = self.__dataEx[3]           # 4. Servo ID
        self.__cmd = self.__dataEx[4]           # 5. CMD
        self.__data[0] = self.__dataEx[7]
        self.__data[1] = self.__dataEx[8]
        self.__lengthString = 2

        self.__ck1 = (self.__dataEx[2] ^ self.__dataEx[3] ^
                     self.__dataEx[4] ^ self.__dataEx[7] ^ self.__dataEx[8]) & 0xFE
        self.__ck2 = self.__checksum2()

        if (self.__ck1 != self.__dataEx[5]):
            return -1   # checksum verify
        if (self.__ck2 != self.__dataEx[6]):
            return -2

        return self.__dataEx[7]			# return status

    # torque on -
    def torqueON(self, servoID):
        self.__pSize = 0x0A               # 3.Packet size 7-58
        self.__pID = servoID            # 4. Servo ID
        self.__cmd = self.__HRAMWRITE          # 5. CMD
        self.__data[0] = 0x34               # 8. Address
        self.__data[1] = 0x01               # 9. Length
        self.__data[2] = 0x60               # 10. 0x60=Torque ON
        self.__lengthString = 3             # lenghtData

        self.__ck1 = self.__checksum1(self.__data, self.__lengthString)  # 6. Checksum1
        self.__ck2 = self.__checksum2()  # 7. Checksum2
        self.__dataEx[0] = 0xFF			# Packet Header
        self.__dataEx[1] = 0xFF			# Packet Header
        self.__dataEx[2] = self.__pSize	 		# Packet Size
        self.__dataEx[3] = self.__pID			# Servo ID
        self.__dataEx[4] = self.__cmd			# Command Ram Write
        self.__dataEx[5] = self.__ck1			# Checksum 1
        self.__dataEx[6] = self.__ck2			# Checksum 2
        self.__dataEx[7] = self.__data[0] 		# Address 52
        self.__dataEx[8] = self.__data[1] 		# Length
        self.__dataEx[9] = self.__data[2] 		# Torque ON
        self.__sendData()

    # torque off - the torque is FREE, not Break
    def torqueOFF(self, servoID):
        self.__pSize = 0x0A               # 3.Packet size 7-58
        self.__pID = servoID            # 4. Servo ID
        self.__cmd = self.__HRAMWRITE          # 5. CMD
        self.__data[0] = 0x34               # 8. Address
        self.__data[1] = 0x01               # 9. Lenght
        self.__data[2] = 0x00               # 10. 0x00=Torque Free
        self.__lengthString = 3             # lenghtData

        self.__ck1 = self.__checksum1(self.__data, self.__lengthString)  # 6. Checksum1
        self.__ck2 = self.__checksum2()  # 7. Checksum2

        self.__dataEx[0] = 0xFF			# Packet Header
        self.__dataEx[1] = 0xFF			# Packet Header
        self.__dataEx[2] = self.__pSize	 		# Packet Size
        self.__dataEx[3] = self.__pID			# Servo ID
        self.__dataEx[4] = self.__cmd			# Command Ram Write
        self.__dataEx[5] = self.__ck1			# Checksum 1
        self.__dataEx[6] = self.__ck2			# Checksum 2
        self.__dataEx[7] = self.__data[0] 		# Address 52
        self.__dataEx[8] = self.__data[1] 		# Length
        self.__dataEx[9] = self.__data[2]  # length


        self.__sendData()

    # ACK  - 0=No Replay, 1=Only reply to READ CMD, 2=Always reply
    def ACK(self, valueACK):
        self.__pSize = 0x0A               # 3.Packet size 7-58
        self.__pID = 0xFE	            # 4. Servo ID
        self.__cmd = self.__HRAMWRITE          # 5. CMD
        self.__data[0] = 0x34               # 8. Address
        self.__data[1] = 0x01               # 9. length
        # 10.Value. 0=No Replay, 1=Only reply to READ CMD, 2=Always reply
        self.__data[2] = valueACK
        self.__lengthString = 3             # lengthData

        self.__ck1 = self.__checksum1(self.__data, self.__lengthString)  # 6. Checksum1
        self.__ck2 = self.__checksum2()  # 7. Checksum2

        self.__dataEx[0] = 0xFF			# Packet Header
        self.__dataEx[1] = 0xFF			# Packet Header
        self.__dataEx[2] = self.__pSize	 		# Packet Size
        self.__dataEx[3] = self.__pID			# Servo ID
        self.__dataEx[4] = self.__cmd			# Command Ram Write
        self.__dataEx[5] = self.__ck1			# Checksum 1
        self.__dataEx[6] = self.__ck2			# Checksum 2
        self.__dataEx[7] = self.__data[0] 		# Address 52
        self.__dataEx[8] = self.__data[1] 		# Length
        self.__dataEx[9] = self.__data[2] 		# Value
        self.__sendData()

    # model - 1=0101 - 2=0201
    def model(self):
        self.__pSize = 0x09               # 3.Packet size 7-58
        self.__pID = 0xFE	            # 4. Servo ID
        self.__cmd = self.__HEEPREAD           # 5. CMD
        self.__data[0] = 0x00               # 8. Address
        self.__data[1] = 0x01               # 9. Lenght
        self.__lengthString = 2             # lenghtData

        self.__ck1 = self.__checksum1(self.__data, self.__lengthString)  # 6. Checksum1
        self.__ck2 = self.__checksum2()  # 7. Checksum2

        self.__dataEx[0] = 0xFF			# Packet Header
        self.__dataEx[1] = 0xFF			# Packet Header
        self.__dataEx[2] = self.__pSize	 		# Packet Size
        self.__dataEx[3] = self.__pID			# Servo ID
        self.__dataEx[4] = self.__cmd			# Command Ram Write
        self.__dataEx[5] = self.__ck1			# Checksum 1
        self.__dataEx[6] = self.__ck2			# Checksum 2
        self.__dataEx[7] = self.__data[0] 		# Address
        self.__dataEx[8] = self.__data[1] 		# Length

        self.__sendData()

        sleep(0.001)
        self.__readData(9)

        self.__pSize = self.__dataEx[2]             # 3.Packet size 7-58
        self.__pID = self.__dataEx[3]             # 4. Servo ID
        self.__cmd = self.__dataEx[4]             # 5. CMD
        self.__data[0] = self.__dataEx[7]       # 8. 1st byte
        self.__lengthString = 1                # lenghtData

        self.__ck1 = self.__checksum1(self.__data, self.__lengthString)  # 6. Checksum1
        self.__ck2 = self.__checksum2()  # 7. Checksum2

        if (self.__ck1 != self.__dataEx[5]):
            return -1  # checksum verify
        if (self.__ck2 != self.__dataEx[6]):
            return -2

        return self.__dataEx[7]			# return status

    def set_ID(self, ID_Old, ID_New):
        self.__pSize = 0x0A               # 3.Packet size 7-58
        self.__pID = ID_Old		        # 4. Servo ID OLD - original servo ID
        self.__cmd = self.__HEEPWRITE          # 5. CMD
        self.__data[0] = 0x06               # 8. Address
        self.__data[1] = 0x01               # 9. Lenght
        self.__data[2] = ID_New             # 10. ServoID NEW
        self.__lengthString = 3             # lenghtData

        self.__ck1 = self.__checksum1(self.__data, self.__lengthString)  # 6. Checksum1
        self.__ck2 = self.__checksum2()  # 7. Checksum2

        self.__dataEx[0] = 0xFF			# Packet Header
        self.__dataEx[1] = 0xFF			# Packet Header
        self.__dataEx[2] = self.__pSize	 		# Packet Size
        self.__dataEx[3] = self.__pID			# Servo ID
        self.__dataEx[4] = self.__cmd			# Command Ram Write
        self.__dataEx[5] = self.__ck1			# Checksum 1
        self.__dataEx[6] = self.__ck2			# Checksum 2
        self.__dataEx[7] = self.__data[0] 		# Address 52
        self.__dataEx[8] = self.__data[1] 		# Length
        self.__dataEx[9] = self.__data[2] 		# Value

        self.__sendData()

    def clearError(self, servoID):
        self.__pSize = 0x0B               # 3.Packet size 7-58
        self.__pID = servoID     		# 4. Servo ID - 253=all servos
        self.__cmd = self.__HRAMWRITE          # 5. CMD
        self.__data[0] = 0x30               # 8. Address
        self.__data[1] = 0x02               # 9. length
        self.__data[2] = 0x00               # 10. Write error=0
        self.__data[3] = 0x00               # 10. Write detail error=0

        self.__lengthString = 4             # lengthData

        self.__ck1 = self.__checksum1(self.__data, self.__lengthString)  # 6. Checksum1
        self.__ck2 = self.__checksum2()  # 7. Checksum2

        self.__dataEx[0] = 0xFF			# Packet Header
        self.__dataEx[1] = 0xFF			# Packet Header
        self.__dataEx[2] = self.__pSize	 		# Packet Size
        self.__dataEx[3] = self.__pID			# Servo ID
        self.__dataEx[4] = self.__cmd			# Command Ram Write
        self.__dataEx[5] = self.__ck1			# Checksum 1
        self.__dataEx[6] = self.__ck2			# Checksum 2
        self.__dataEx[7] = self.__data[0] 		# Address 52
        self.__dataEx[8] = self.__data[1] 		# Length
        self.__dataEx[9] = self.__data[2] 		# Value1
        self.__dataEx[10] = self.__data[3] 		# Value2
        self.__sendData()
# -----------------------------------

    def moveAll(self, servoID, Goal, iLed):
        if (Goal > 1023 or Goal < 0):
            return  # 0 <--> 1023 range

        iMode = 0  # mode=position
        iStop = 0  # stop=0

        # Position definition
        posLSB = Goal & 0X00FF				# MSB Pos
        posMSB = (Goal & 0XFF00) >> 8			# LSB Pos

        # led
        SetValue = iStop + iMode * 2 + \
            self.__ledset[iLed][0] * 4 + self.__ledset[iLed][1] * \
            8 + self.__ledset[iLed][2] * 16  # assign led value

        # add servo data to list, pos mode
        self.__addData(posLSB, posMSB, SetValue, servoID)

# move all servo at the same time to a position: servo list building
    def moveAllAngle(self, servoID, angle, iLed):
        if (angle > 160.0 or angle < -160.0):
            return      # out of the range
        position = int(angle / 0.325) + 512
        self.__moveAll(servoID, position, iLed)

# move all servo at the same time with different speeds: servo list building
    def moveSpeedAll(self, servoID, Goal, iLed):
        if (Goal > 1023 or Goal < -1023):
            return  # -1023 <--> 1023 range

        iMode = 1                  		# mode=continous rotation
        iStop = 0                  		# Stop=0

        # Speed definition
        GoalSpeedSign = 0
        if (Goal < 0):
            GoalSpeedSign = (-1) * Goal
            GoalSpeedSign |= 0x4000  # bit n�14
        else:
            GoalSpeedSign = Goal

        speedGoalLSB = GoalSpeedSign & 0X00FF 	      		 # MSB speedGoal
        speedGoalMSB = (GoalSpeedSign & 0xFF00) >> 8        # LSB speedGoal

        # led
        SetValue = iStop + iMode * 2 + \
            self.__ledset[iLed][0] * 4 + self.__ledset[iLed][1] * \
            8 + self.__ledset[iLed][2] * 16  # assign led value

        # add servo data to list, speed mode
        self.__addData(speedGoalLSB, speedGoalMSB, SetValue, servoID)

# move all servo with the same execution time
    def actionAll(self, pTime):
        if ((pTime < 0) or (pTime > 2856)):
            return

        self.__pSize = 0x08 + self.__conta     	    # 3.Packet size 7-58
        self.__cmd = self.__HSJOG		 			# 5. CMD SJOG Write n servo with same execution time
        self.__playTime = int(float(pTime) / 11.2)  # 8. Execution time

        self.__pID = 0xFE ^ self.__playTime
        self.__ck1 = self.__checksum1(self.__moveData, self.__conta)  # 6. Checksum1
        self.__ck2 = self.__checksum2()  # 7. Checksum2

        self.__pID = 0xFE
        self.__dataEx[0] = 0xFF				# Packet Header
        self.__dataEx[1] = 0xFF				# Packet Header
        self.__dataEx[2] = self.__pSize	 			# Packet Size
        self.__dataEx[3] = self.__pID				# Servo ID
        self.__dataEx[4] = self.__cmd				# Command Ram Write
        self.__dataEx[5] = self.__ck1				# Checksum 1
        self.__dataEx[6] = self.__ck2				# Checksum 2
        self.__dataEx[7] = self.__playTime			# Execution time

        for i in range(self.__conta):
            # Variable servo data
            self.__dataEx[i + 8] = self.__moveData[i]

        self.__sendData()

        self.__conta = 0 						# reset counter

    # get Position
    def getPosition(self, servoID):
        Position = 0

        self.__pSize = 0x09               # 3.Packet size 7-58
        self.__pID = servoID     	    # 4. Servo ID - 253=all servos
        self.__cmd = self.__HRAMREAD           # 5. CMD
        self.__data[0] = 0x3A               # 8. Address
        self.__data[1] = 0x02               # 9. Lenght

        self.__lengthString = 2             # lenghtData

        self.__ck1 = self.__checksum1(self.__data, self.__lengthString)  # 6. Checksum1
        self.__ck2 = self.__checksum2()  # 7. Checksum2

        self.__dataEx[0] = 0xFF			# Packet Header
        self.__dataEx[1] = 0xFF			# Packet Header
        self.__dataEx[2] = self.__pSize	 		# Packet Size
        self.__dataEx[3] = self.__pID			# Servo ID
        self.__dataEx[4] = self.__cmd			# Command Ram Write
        self.__dataEx[5] = self.__ck1			# Checksum 1
        self.__dataEx[6] = self.__ck2			# Checksum 2
        self.__dataEx[7] = self.__data[0]      	# Address
        self.__dataEx[8] = self.__data[1] 		# Length

        self.__sendData()

        sleep(0.001)
        self.__readData(13)

        self.__pSize = self.__dataEx[2]           # 3.Packet size 7-58
        self.__pID = self.__dataEx[3]           # 4. Servo ID
        self.__cmd = self.__dataEx[4]           # 5. CMD
        self.__data[0] = self.__dataEx[7]
        self.__data[1] = self.__dataEx[8]
        self.__data[2] = self.__dataEx[9]
        self.__data[3] = self.__dataEx[10]
        self.__data[4] = self.__dataEx[11]
        self.__data[5] = self.__dataEx[12]
        self.__lengthString = 6

        self.__ck1 = self.__checksum1(self.__data, self.__lengthString)  # 6. Checksum1
        self.__ck2 = self.__checksum2()  # 7. Checksum2

        if (self.__ck1 != self.__dataEx[5]):
            return -1
        if (self.__ck2 != self.__dataEx[6]):
            return -1

        Position = ((self.__dataEx[10] & 0x03) << 8) | self.__dataEx[9]
        return Position

    def getAngle(self, servoID):
        pos = int(self.getPosition(servoID))
        return (pos - 512) * 0.325

# reboot single servo - pay attention 253 - all servos doesn't work!
    def reboot(self, servoID):
        self.__pSize = 0x07               # 3.Packet size 7-58
        self.__pID = servoID     	    # 4. Servo ID - 253=all servos
        self.__cmd = self.__HREBOOT            # 5. CMD
        self.__ck1 = (self.__pSize ^ self.__pID ^ self.__cmd) & 0xFE
        self.__ck2 = (~(self.__pSize ^ self.__pID ^ self.__cmd)) & 0xFE

        self.__dataEx[0] = 0xFF			# Packet Header
        self.__dataEx[1] = 0xFF			# Packet Header
        self.__dataEx[2] = self.__pSize	 		# Packet Size
        self.__dataEx[3] = self.__pID			# Servo ID
        self.__dataEx[4] = self.__cmd			# Command Ram Write
        self.__dataEx[5] = self.__ck1			# Checksum 1
        self.__dataEx[6] = self.__ck2			# Checksum 2

        self.__sendData()

# ------------------------------------
    #  LED  - see table of colors
    def setLed(self, servoID, valueLed):
        self.__pSize = 0x0A               # 3.Packet size 7-58
        self.__pID = servoID            # 4. Servo ID
        self.__cmd = self.__HRAMWRITE          # 5. CMD
        self.__data[0] = 0x35               # 8. Address 53
        self.__data[1] = 0x01               # 9. Lenght
        self.__data[2] = valueLed           # 10.LedValue
        self.__lenghtString = 3               # lenghtData

        self.__ck1 = self.__checksum1(self.__data, self.__lengthString)  # 6. Checksum1
        self.__ck2 = self.__checksum2()  # 7. Checksum2

        self.__dataEx[0] = 0xFF			# Packet Header
        self.__dataEx[1] = 0xFF			# Packet Header
        self.__dataEx[2] = self.__pSize	 		# Packet Size
        self.__dataEx[3] = self.__pID			# Servo ID
        self.__dataEx[4] = self.__cmd			# Command Ram Write
        self.__dataEx[5] = self.__ck1			# Checksum 1
        self.__dataEx[6] = self.__ck2			# Checksum 2
        self.__dataEx[7] = self.__data[0]        # Address
        self.__dataEx[8] = self.__data[1]       	# Length
        self.__dataEx[9] = self.__data[2]        # Value

        self.__sendData()
# ****************************

    def getSpeed(self, servoID):
        speedy = 0

        self.__pSize = 0x09               # 3.Packet size 7-58
        self.__pID = servoID     	   	  # 4. Servo ID
        self.__cmd = self.__HRAMREAD           # 5. CMD
        self.__data[0] = 0x40               # 8. Address
        self.__data[1] = 0x02               # 9. Lenght

        self.__lengthString = 2             # lengthData

        self.__ck1 = self.__checksum1(self.__data, self.__lengthString)  # 6. Checksum1
        self.__ck2 = self.__checksum2()  # 7. Checksum2

        self.__dataEx[0] = 0xFF			# Packet Header
        self.__dataEx[1] = 0xFF			# Packet Header
        self.__dataEx[2] = self.__pSize		# Packet Size
        self.__dataEx[3] = self.__pID			# Servo ID
        self.__dataEx[4] = self.__cmd			# Command Ram Write
        self.__dataEx[5] = self.__ck1			# Checksum 1
        self.__dataEx[6] = self.__ck2			# Checksum 2
        self.__dataEx[7] = self.__data[0] 	    # Address
        self.__dataEx[8] = self.__data[1] 		# Length

        self.__sendData()

        sleep(0.001)
        self.__readData(13)

        self.__pSize = self.__dataEx[2]           # 3.Packet size 7-58
        self.__pID = self.__dataEx[3]           # 4. Servo ID
        self.__cmd = self.__dataEx[4]           # 5. CMD
        self.__data[0] = self.__dataEx[7]
        self.__data[1] = self.__dataEx[8]
        self.__data[2] = self.__dataEx[9]
        self.__data[3] = self.__dataEx[10]
        self.__data[4] = self.__dataEx[11]
        self.__data[5] = self.__dataEx[12]
        self.__lengthString = 6

        self.__ck1 = self.__checksum1(self.__data, self.__lengthString)  # 6. Checksum1
        self.__ck2 = self.__checksum2()  # 7. Checksum2

        if (self.__ck1 != self.__dataEx[5]):
            return -1
        if (self.__ck2 != self.__dataEx[6]):
            return -1

        speedy = ((self.__dataEx[10] & 0xFF) << 8) | self.__dataEx[9]

        return speedy


# move one servo with continous rotation
    def moveSpeedOne(self, servoID, Goal, pTime, iLed):
        if (Goal > 1023 or Goal < -1023):
            return              # speed (goal) non correct
        if ((pTime < 0) or (pTime > 2856)):
            return

        GoalSpeedSign
        if (Goal < 0):
            GoalSpeedSign = (-1) * Goal
            GoalSpeedSign |= 0x4000  # bit n�14
        else:
            GoalSpeedSign = Goal
        speedGoalLSB = GoalSpeedSign & 0X00FF 		       # MSB speedGoal
        speedGoalMSB = (GoalSpeedSign & 0xFF00) >> 8      # LSB speedGoal

        # led
        SetValue = 2 + self.__ledset[iLed][0] * 4 + self.__ledset[iLed][1] * \
            8 + self.__ledset[iLed][2] * 16  # assign led value

        self.__playTime = int(float(pTime) / 11.2)				# 8. Execution time

        self.__pSize = 0x0C              					# 3.Packet size 7-58
        self.__cmd = self.__HSJOG      					        # 5. CMD

        self.__data[0] = speedGoalLSB            			    # 8. speedLSB
        self.__data[1] = speedGoalMSB              			# 9. speedMSB
        self.__data[2] = SetValue                          	# 10. Mode=0
        self.__data[3] = servoID                    			# 11. ServoID

        self.__pID = servoID ^ self.__playTime

        self.__lengthString = 4             					# lenghtData

        self.__ck1 = self.__checksum1(self.__data, self.__lengthString)  # 6. Checksum1
        self.__ck2 = self.__checksum2()  # 7. Checksum2

        self.__pID = servoID

        self.__dataEx[0] = 0xFF				# Packet Header
        self.__dataEx[1] = 0xFF				# Packet Header
        self.__dataEx[2] = self.__pSize	 		# Packet Size
        self.__dataEx[3] = self.__pID				# Servo ID
        self.__dataEx[4] = self.__cmd				# Command Ram Write
        self.__dataEx[5] = self.__ck1				# Checksum 1
        self.__dataEx[6] = self.__ck2				# Checksum 2
        self.__dataEx[7] = self.__playTime  		# Execution time
        self.__dataEx[8] = self.__data[0]
        self.__dataEx[9] = self.__data[1]
        self.__dataEx[10] = self.__data[2]
        self.__dataEx[11] = self.__data[3]

        self.__sendData()

# move one servo at goal position 0 - 1024
    def moveOne(self, servoID, Goal, pTime, iLed):
        if (Goal > 1023 or Goal < 0):
            return              # speed (goal) non correct
        if ((pTime < 0) or (pTime > 2856)):
            return

        # Position definition
        posLSB = Goal & 0x00FF								# MSB Pos
        posMSB = (Goal & 0xFF00) >> 8						# LSB Pos

        # led
        SetValue = self.__ledset[iLed][0] * 4 + self.__ledset[iLed][1] * \
            8 + self.__ledset[iLed][2] * 16  # assign led value

        self.__playTime = int(float(pTime) / 11.2)			# 8. Execution time

        self.__pSize = 0x0C          			    	# 3.Packet size 7-58
        self.__cmd = self.__HSJOG              				# 5. CMD

        self.__data[0] = posLSB               			# 8. speedLSB
        self.__data[1] = posMSB               			# 9. speedMSB
        self.__data[2] = SetValue                         # 10. Mode=0
        self.__data[3] = servoID                    		# 11. ServoID

        self.__pID = servoID ^ self.__playTime

        self.__lengthString = 4             				# lengthData

        self.__ck1 = self.__checksum1(self.__data, self.__lengthString)  # 6. Checksum1
        self.__ck2 = self.__checksum2()  # 7. Checksum2

        self.__pID = servoID

        self.__dataEx[0] = 0xFF				# Packet Header
        self.__dataEx[1] = 0xFF				# Packet Header
        self.__dataEx[2] = self.__pSize	 		# Packet Size
        self.__dataEx[3] = self.__pID				# Servo ID
        self.__dataEx[4] = self.__cmd				# Command Ram Write
        self.__dataEx[5] = self.__ck1				# Checksum 1
        self.__dataEx[6] = self.__ck2				# Checksum 2
        self.__dataEx[7] = self.__playTime  		# Execution time
        self.__dataEx[8] = self.__data[0]
        self.__dataEx[9] = self.__data[1]
        self.__dataEx[10] = self.__data[2]
        self.__dataEx[11] = self.__data[3]

        self.__sendData()

# move one servo to an angle between -160 and 160
    def moveOneAngle(int servoID, float angle, int pTime, int iLed):
    	if (angle > 160.0or angle < -160.0):
            return
    	position = int(angle / 0.325) + 512
    	moveOne(servoID, position, pTime, iLed)

# write registry in the RAM: one byte
    def writeRegistryRAM(self, servoID, address, writeByte):
        self.__pSize = 0x0A               	# 3.Packet size 7-58
        self.__pID = servoID     			# 4. Servo ID - 253=all servos
        self.__cmd = self.__HRAMWRITE          	# 5. CMD
        self.__data[0] = address              # 8. Address
        self.__data[1] = 0x01               	# 9. Lenght
        self.__data[2] = writeByte            # 10. Write error=0

        self.__lengthString = 3             	# lenghtData

        self.__ck1 = self.__checksum1(self.__data, self.__lengthString)  # 6. Checksum1
        self.__ck2 = self.__checksum2()  # 7. Checksum2

        self.__dataEx[0] = 0xFF			# Packet Header
        self.__dataEx[1] = 0xFF			# Packet Header
        self.__dataEx[2] = self.__pSize	 	# Packet Size
        self.__dataEx[3] = self.__pID			# Servo ID
        self.__dataEx[4] = self.__cmd			# Command Ram Write
        self.__dataEx[5] = self.__ck1			# Checksum 1
        self.__dataEx[6] = self.__ck2			# Checksum 2
        self.__dataEx[7] = self.__data[0] 		# Address 52
        self.__dataEx[8] = self.__data[1] 		# Length
        self.__dataEx[9] = self.__data[2] 		# Value1
        self.__dataEx[10] = self.__data[3] 		# Value2

        self.__sendData()

# write registry in the EEP memory (ROM): one byte
    def writeRegistryEEP(self, servoID, address, writeByte):
        self.__pSize = 0x0A                  # 3.Packet size 7-58
        self.__pID = servoID     	         # 4. Servo ID - 253=all servos
        self.__cmd = self.__HEEPWRITE             # 5. CMD
        self.__data[0] = address               # 8. Address
        self.__data[1] = 0x01                  # 9. Lenght
        self.__data[2] = writeByte             # 10. Write error=0

        self.__lengthString = 3           	 # lenghtData

        self.__ck1 = self.__checksum1(self.__data, self.__lengthString)  # 6. Checksum1
        self.__ck2 = self.__checksum2()  # 7. Checksum2

        self.__dataEx[0] = 0xFF			# Packet Header
        self.__dataEx[1] = 0xFF			# Packet Header
        self.__dataEx[2] = self.__pSize		# Packet Size
        self.__dataEx[3] = self.__pID			# Servo ID
        self.__dataEx[4] = self.__cmd			# Command Ram Write
        self.__dataEx[5] = self.__ck1			# Checksum 1
        self.__dataEx[6] = self.__ck2			# Checksum 2
        self.__dataEx[7] = self.__data[0] 		# Address 52
        self.__dataEx[8] = self.__data[1] 		# Length
        self.__dataEx[9] = self.__data[2] 		# Value1
        self.__dataEx[10] = self.__data[3] 		# Value2

        self.__sendData()

# ****************************
# Private Methods ############################

    def __checksum1(self, data, lengthString):
        self.__XOR = 0
        self.__XOR = self.__XOR ^ self.__pSize
        self.__XOR = self.__XOR ^ self.__pID
        self.__XOR = self.__XOR ^ self.__cmd
        for i in range(lengthString):
            self.__XOR = self.__XOR ^ data[i]
        return self.__XOR & 0xFE

    def __checksum2(self):
        return (~self.__XOR) & 0xFE

    def __addData(GoalLSB, GoalMSB, set, servoID):
        self.__moveData[self.__conta] = GoalLSB
        self.__conta += 1
        self.__moveData[self.__conta] = GoalMSB
        self.__conta += 1
        self.__moveData[self.__conta] = set
        self.__conta += 1
        self.__moveData[self.__conta] = servoID
        self.__conta += 1

    def __sendData(self):
        self.__clearBuffer()  # clear the serialport buffer - try to do it!
        self.__ser.write(self.__dataEx[:self.__pSize])
        sleep(0.001)

    def __readData(self, size):
        self.__dataEx = self.__ser.read(size)

    def __clearBuffer(self):
        self.__ser.reset_input_buffer()
        sleep(0.002)


"""@classmethod
    def connect(cls, id):
        self.__ser=appserial.connect(port,baud)
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
