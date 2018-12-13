import appserial
from time import sleep

class herkulex(object):
    """docstring for herkulex."""
    def __init__(self, port, baud):
        super(herkulex, self).__init__()
        self.port = port
        self.baud = baud
    @classmethod
    def connect(cls, id):
        self.ser=appserial.connect(port,baud)
        return cls(id, id)

    """@staticmethod
    def getid(brd_id):
        return brd_id"""

    @classmethod
    def getid(cls, brd_id):
        appserial.send()
        input=appserial.read()
        return cls()
