import appserial
from time import sleep

while True:
    appserial.send(0xFF)
    sleep(1)
