import serial.tools.list_ports

def select():
    ports = list(serial.tools.list_ports.comports())

    for p in range(len(ports)):
        print(p, end=' ')
        print(ports[p])
    print('Select port from list')
    p = ports[int(input())]
    return p

"""import serial
import serial.tools.list_ports
ports = list(serial.tools.list_ports.comports())

for p in ports:
    print(p)
    if "ELTIMA" in p[1]:
        print("This is an Eltima!")
        ser=serial.Serial(p[0],115200)
        ser.write(b"hello")
"""
