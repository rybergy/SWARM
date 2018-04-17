import struct
from serial import Serial
from .link import *


class SendOp(OpCode):
    NEW_GPS = b'\0'
    CONTROL = b'\1'
    FORCE_DIRECTION = b'\2'


class RecvOp(OpCode):
    ERROR = b'\0'
    DEBUG = b'\1'
    STATUS = b'\2'
    GPS = b'\3'


class ArduinoPacket(Packet):
    """
    Pass fmt into constructor to override format used.
    """

    def pack(self):
        if self.data is None:  # process data

            # ensure we have a code
            if self.code is None:
                raise MalformedData("No OpCode packed")

            # ensure we have a format
            try:
                fmt = self.options['fmt']
            except KeyError:
                raise MalformedData("No Format to pack with")

            # special 'string' case and general case.
            # look up struct.pack for details on fmt string
            if fmt == 'STRING':
                self.data = self.code.value + self.values[0].encode('utf-8')
            else:
                self.data = self.code.value + struct.pack(fmt, *self.values)

        # return data, whether we processed it now or earlier
        return self.data

    def get_code(self):
        if self.code is None:
            self.code = RecvOp(self.data[:1])
        return self.code

    def unpack(self):
        if len(self.values) == 0:  # if we have no values yet, process them

            # ensure we have a format
            try:
                fmt = self.options['fmt']
            except KeyError:
                raise MalformedData("No Format to pack with")

            # special 'string' case and general case.
            # look up struct.pack for details on fmt string
            if fmt == 'STRING':
                self.values = [self.data[1:].decode('utf-8')]
            else:
                self.values = struct.unpack(fmt, self.data[1:])

        # return values, whether we processed them now or earlier
        return self.values


class Arduino(Link):
    """
    Handles communication with the Arduino.
    """

    def __init__(self, bot, config):
        super(Arduino, self).__init__(bot, config)
        self.serial = Serial(self.config['port'], self.config['baud'], timeout=5)

    def write(self, packet: Packet):
        self.serial.write(packet.pack())  # get data from packet and send it

    def read(self):
        b = b''  # buffer
        while self.running:
            v = self.serial.read()  # get a byte
            b += v  # add it to the buffer
            if v == b'\n':  # if this byte is a newline, we are done reading
                return ArduinoPacket(data=b)

    @send_op(SendOp.FORCE_DIRECTION, fmt='STRING')
    def force_direction(self, direction: str):
        """
        Debugging/testing method.
        Forces the IR sensors on the bot to return that it should go in a specific direction.
        """
        assert direction in ['stop', 'forward', 'backward', 'left', 'right', 'auto']
        return ArduinoPacket(direction)

    @send_op(SendOp.CONTROL, fmt='<ff')
    def control(self, left, right):
        """
        Set the bot's wheel velocities manually. left and right are 1-100 percentages
        """
        assert 1 < left < 100
        assert 1 < right < 100
        return ArduinoPacket(left / 100.0, right / 100.0)

    @send_op(SendOp.NEW_GPS, fmt='ff')
    def new_gps(self, lat, lon):
        """
        Set the bot's new gps goal.
        """
        return ArduinoPacket(lat, lon)

    @recv_op(RecvOp.DEBUG, fmt='STRING')
    def debug(self, s, **options):
        """
        Received debug info from bot. Simple echo.
        """
        print("DEBUG: {}".format(s), end='', flush=True)

    @recv_op(RecvOp.ERROR, fmt='STRING')
    def error(self, s, **options):
        """
        Received error info from bot. Simple echo.
        """
        print("ERROR: {}".format(s[0]), end='', flush=True)

    @recv_op(RecvOp.STATUS, fmt='STRING')
    def status(self, s, **options):
        """
        Received status info from bot. Simple echo.
        """
        print("STATUS: {}".format(s[0]), end='', flush=True)

    @recv_op(RecvOp.GPS, fmt='ff')
    def recv_gps(self, lat, lon, **options):
        """
        Received gps info from bot. Simple echo.
        """
        print("GPS: {}, {}".format(lat, lon), end='', flush=True)
