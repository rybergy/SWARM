import struct
from serial import Serial
from .link import *


class SendOp(OpCode):
    NEW_GPS = b'\0'
    CONTROL = b'\1'
    FORCE_DIRECTION = b'\2'
    MODE = b'\3'


class RecvOp(OpCode):
    RECEIVED = b'\0'
    ERROR = b'\1'
    DEBUG = b'\2'
    STATUS = b'\3'
    GPS = b'\4'


class ArduinoPacket(Packet):
    """
    Pass fmt into constructor to override format used.
    """

    def pack(self):
        if self.data is None:  # process data
            # ensure we have a format
            try:
                fmt = self.options['fmt']
            except KeyError:
                raise MalformedData("No Format to pack with")

            # special 'string', and 'nothing, cases and general case.
            # look up struct.pack for details on fmt string
            if fmt == 'STRING':
                self.data = self.get_code().value + self.values[0].encode('utf-8')
            elif fmt == 'NOTHING':
                self.data = self.get_code().value
            else:
                self.data = self.get_code().value + struct.pack(fmt, *self.values)

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

            # special 'string' case, 'nothing' case, and general case.
            # look up struct.pack for details on fmt string
            if fmt == 'STRING':
                self.values = [self.data[1:].decode('utf-8')]
            elif fmt == 'NOTHING':
                self.values = []
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
        self.ready_to_send = False

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

    @send_op(SendOp.CONTROL, fmt='hh')
    def control(self, left: int, right: int):
        """
        Set the bot's wheel velocities manually.
        left and right are 0-200 representing percentages. 0-99 is backward, 100 is stop, 101-200 is forward
        """
        assert 0 < left < 200
        assert 0 < right < 200
        print("Control command sent to arduino: {}, {}". format(left, right))
        return ArduinoPacket(left, right)

    @send_op(SendOp.NEW_GPS, fmt='ff')
    def new_gps(self, lat: float, lon: float):
        """
        Set the bot's new gps goal.
        """
        return ArduinoPacket(lat, lon)

    @send_op(SendOp.MODE, fmt='h')
    def set_mode(self, mode: int):
        """
        Set the bot's mode.
        -1 - WAITING
         0 - NAVIGATION
         1 - FOLLOW
         2 - MANUAL
        """
        return ArduinoPacket(mode)

    @recv_op(RecvOp.RECEIVED, fmt='NOTHING')
    def command_received(self, **_):
        """
        The bot received a command and is ready to receive more.
        """
        self.ready_to_send = True

    @recv_op(RecvOp.DEBUG, fmt='STRING')
    def debug(self, s, **_):
        """
        Received debug info from bot. Simple echo.
        """
        print("DEBUG: {}".format(s), end='', flush=True)

    @recv_op(RecvOp.ERROR, fmt='STRING')
    def error(self, s, **_):
        """
        Received error info from bot. Simple echo.
        """
        print("ERROR: {}".format(s[0]), end='', flush=True)

    @recv_op(RecvOp.STATUS, fmt='STRING')
    def status(self, s, **_):
        """
        Received status info from bot. Simple echo.
        """
        print("STATUS: {}".format(s[0]), end='', flush=True)

    @recv_op(RecvOp.GPS, fmt='ff')
    def recv_gps(self, lat, lon, **_):
        """
        Received gps info from bot. Simple echo.
        """
        print("GPS: {}, {}".format(lat, lon), end='', flush=True)
