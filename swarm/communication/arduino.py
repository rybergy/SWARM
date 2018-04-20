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


class Arduino(Link):
    """
    Handles communication with the Arduino.
    """

    ReceiveOpType = RecvOp

    def __init__(self, bot, config):
        super(Arduino, self).__init__(bot, config)
        self.serial = Serial(self.config['port'], self.config['baud'], timeout=5)

    def stop(self):
        super(Arduino, self).stop()
        self.serial.close()

    def write(self, packet: Packet):
        self.serial.write(packet.pack())  # get data from packet and send it
        self.ready_to_send = False

    def read(self):
        b = b''  # buffer
        while self.running:
            v = self.serial.read()  # get a byte
            b += v  # add it to the buffer
            if v == b'\n':  # if this byte is a newline, we are done reading
                return Packet(data=b)

    @send_op(SendOp.FORCE_DIRECTION, fmt='STRING')
    def force_direction(self, direction: str):
        """
        Debugging/testing method.
        Forces the IR sensors on the bot to return that it should go in a specific direction.
        """
        assert direction in ['stop', 'forward', 'backward', 'left', 'right', 'auto']
        return Packet(direction)

    @send_op(SendOp.CONTROL, fmt='fff')
    def control(self, left: float, right: float, duration: float):
        """
        Set the bot's wheel velocities manually.
        left and right are floats in the range +-1, percentage of velocity for each side.
        duration is the duration this command should be run for on the arduino (in seconds).
        """
        # print("Control command sent to arduino: {}, {}". format(left, right))
        return Packet(left, right, duration)

    @send_op(SendOp.NEW_GPS, fmt='ff')
    def new_gps(self, lat: float, lon: float):
        """
        Set the bot's new gps goal.
        """
        return Packet(lat, lon)

    @send_op(SendOp.MODE, fmt='h')
    def set_mode(self, mode: int):
        """
        Set the bot's mode.
        -1 - WAITING
         0 - NAVIGATION
         1 - FOLLOW
         2 - MANUAL
        """
        return Packet(mode)

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
