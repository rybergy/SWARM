import struct

from serial import Serial

from .link import Link


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
