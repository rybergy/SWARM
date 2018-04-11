import struct
from serial import Serial

from .link import *


class SendOp(OpCode):
    NEW_GPS = b'\0'


class RecvOp(OpCode):
    ERROR = b'\0'
    DEBUG = b'\1'
    STATUS = b'\2'
    GPS = b'\3'

fmts = {
    RecvOp.ERROR: '',
    RecvOp.DEBUG: '',
    RecvOp.STATUS: '',
    RecvOp.GPS: ''
}


class ArduinoPacket(Packet):

    def __init__(self, *data, fmt=None):
        super(ArduinoPacket, self).__init__(*data, fmt=fmt)

    def pack(self, fmt=None):
        fmt = fmt or self.kwargs['fmt']
        if fmt is None:
            raise MalformedData("No fmt packed")
        if self.code is None:
            raise MalformedData("No OpCode packed")
        return self.code + struct.pack(fmt, *self.data)

    @classmethod
    def unpack(cls, data):
        fmt = fmts[RecvOp(data[0])]
        # TODO: replace Packet unpack/pack logic with embedded functions in the enum



class Arduino(Link):
    """
    Handles communication with the Arduino.
    """

    def __init__(self, bot, config):
        super(Arduino, self).__init__(bot, config)
        self.serial = Serial(config['port'], config('baud'))

    def __wait_for_read(self, fmt):
        """
        Read data based on fmt (see python's struct.pack docs) ('=B' is always prepended)
        """
        return struct.unpack('=B' + fmt, self.serial.read(256))

    def __wait_for_write(self, fmt, *data):
        """
        Writes to the arduino
        fmt is a format string specified in python's struct.pack docs ('=B' is always prepended)
        any further arguments are passed as arguments to struct.pack
        """
        self.serial.write(struct.pack('=B' + fmt, *data))

    async def control(self, direction: int):
        """
        opcode 0
        example send function. intended for direct bot control.
        directions are laid out as on a numpad.
        """
        await self.write('B', 0, direction)  # B = unsigned char


@Arduino.recv_op(0)
async def telemetry(self, *data):
    """
    example telemetry reader. simply prints data
    """
    print(data)
