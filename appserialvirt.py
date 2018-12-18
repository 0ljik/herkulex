import serial
from time import sleep

ser = serial.Serial(port='COM2', baudrate=115200)#, bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None) # Establish the connection on a specific port

#ser.write(packet)
def send(val):
     ser.write(val)#.decode('hex'))
def read():
     # To read from the device
     return ser.read() # Read the newest output from the Arduino
def flush():
    ser.flush()
