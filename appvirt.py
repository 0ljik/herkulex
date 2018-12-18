import appserialvirt
from time import sleep

while True:
    print(hex(ord(appserialvirt.read())))
    sleep(0.001)
