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
herkulex.torqueON(2)
sleep(0.01)
herkulex.setLed(1, herkulex._herkulex__LED_GREEN2)
#print(herkulex.stat(2))
herkulex.moveSpeedOne(2, 1023, 500, 2)
sleep(5)
herkulex.torqueOFF(2)
