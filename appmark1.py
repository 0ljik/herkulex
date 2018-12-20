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
# herkulex.torqueON(1)
sleep(0.01)
herkulex.setLed(2, herkulex._herkulex__LED_GREEN2)
# herkulex.torqueOFF(1)
