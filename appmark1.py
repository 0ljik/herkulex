from xsherkulex import herkulex
from time import sleep
import appserial

herkulex=herkulex("COM1",115200)
herkulex.torqueON(1)
sleep(0.01)
herkulex.torqueOFF(1)
