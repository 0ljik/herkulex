from xsherkulex import herkulex
from time import sleep
# import appserial
import serial.tools.list_ports
ports = list(serial.tools.list_ports.comports())

for p in range(len(ports)):
    print(p, end=' ')
    print(ports[p])
print('Select port from list')
p = ports[int(input())]
herkulex = herkulex(p, 115200)
herkulex.initialize()
#herkulex.torqueON(2)
sleep(0.1)
herkulex.setLed(2, herkulex._herkulex__LED_GREEN2)
sleep(0.1)
#herkulex.moveOneAngle(2, 300, 300, 2)
herkulex.moveOne(2, 512, 200, 2)
sleep(1)
print(herkulex.getPosition(2))
sleep(1)
herkulex.torqueOFF(2)
