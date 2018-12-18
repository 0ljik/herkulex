from xsherkulex import herkulex
from time import sleep
#import appserial
import serial.tools.list_ports
ports = list(serial.tools.list_ports.comports())

for p in ports:
    print('1',end=' ')
    print(p)
print('Select port from list')
p=ports[int(input())-1]
herkulex=herkulex(p,115200)
herkulex.torqueON(1)
sleep(0.01)
herkulex.torqueOFF(1)
