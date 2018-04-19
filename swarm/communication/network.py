from serial import Serial
from xbee import XBee
from xbee.backend.base import TimeoutException

from .link import *


class Op(OpCode):
    DEBUG = b'\0'
    RECEIVED = b'\1'
    CONTROL = b'\2'


class Network(Link):
    """
    Handles communication between bots.
    """

    ReceiveOpType = Op

    def __init__(self, bot, config):
        super(Network, self).__init__(bot, config)
        self.serial = Serial(self.config['port'], self.config['baud'])
        self.xbee = XBee(self.serial)
        self.id = self.at('MY')
        self.name = self.at('NI').decode('utf-8')

    def at(self, command):
        """Helper method for getting AT data from xbee"""
        self.xbee.at(frame_id='A', command=command)
        return self.xbee.wait_read_frame()['parameter']

    def read(self):
        try:
            d = self.xbee.wait_read_frame(timeout=5)
            # print('{} received {} from {}'.format(self.id, d['rf_data'], d['source_addr']))
            if d['source_addr'] == self.id:
                print("ignored self message")
                raise TimeoutError  # just to ignore messages from here
            return Packet(
                data=d['rf_data'],
                address=d['source_addr']
            )
        except TimeoutException:
            raise TimeoutError  # convert to standard Error for our handler

    def write(self, packet: Packet):
        addr = packet.options['address'] or b'\xFF\xFF'
        d = packet.pack()
        # print("Sending {} to {} from {}".format(d, addr, self.id))
        self.xbee.tx(dest_addr=addr, data=d)

    @send_op(Op.DEBUG, fmt='STRING')
    def send_debug(self, message: str, address=None):
        """
        Send a debug message to a specific address.
        If no address is specified, broadcasts to all.
        """
        return Packet(message, address=address)

    @send_op(Op.CONTROL, fmt='hh')
    def send_control(self, left, right, address=None):
        """
        Send a control command to a specific address.
        If no address is specified, broadcasts to all.
        """
        return Packet(left, right, address=address)

    @recv_op(Op.DEBUG, fmt='STRING')
    def recv_debug(self, message, address=None, **_):
        """
        Received a debug message from another xbee.
        For now, simple stdout echo.
        """
        print("DEBUG from({}): {}".format(address, message))

    @recv_op(Op.CONTROL, fmt='hh')
    def recv_control(self, left: int, right: int, **_):
        """
        Received a control command. Pass it along to the arduino.
        """
        self.bot.arduino.control(left, right)
