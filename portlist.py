import serial
import serial.tools.list_ports
ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p)
    if "ELTIMA" in p[1]:
        print("This is an Eltima!")
        ser=serial.Serial(p[0],115200)
        ser.write(b"hello")
