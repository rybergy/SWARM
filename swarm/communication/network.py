import struct
from serial import Serial
from xbee import XBee
from xbee.backend.base import TimeoutException

from .link import *


class Op(OpCode):
    DEBUG = b'\0'
    CONTROL = b'\1'


# TODO: this is the same code as arduino. merge them into parent and make Packet no longer abstract
class XbeePacket(Packet):

    def get_code(self):
        if self.code is None:
            self.code = Op(self.data[:1])
        return self.code

    def pack(self, *kwargs):
        if self.data is None:
            # ensure we have a format
            try:
                fmt = self.options['fmt']
            except KeyError:
                raise MalformedData('No Format to pack with')

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


class Network(Link):
    """
    Handles communication between bots.
    """

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
                raise TimeoutError  # just to ignore messages from ourself
            return XbeePacket(
                data=d['rf_data'],
                address=d['source_addr']
            )
        except TimeoutException:
            raise TimeoutError  # convert to standard Error for our handler

    def write(self, packet: XbeePacket):
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
        return XbeePacket(message, address=address)

    @send_op(Op.CONTROL, fmt='hh')
    def send_control(self, left, right, address=None):
        """
        Send a control command to a specific address.
        If no address is specified, broadcasts to all.
        """
        return XbeePacket(left, right, address=address)

    @recv_op(Op.DEBUG, fmt='STRING')
    def recv_debug(self, message, address=None, **_):
        """
        Received a debug message from another xbee.
        For now, simple stdout echo.
        """
        print("DEBUG from({}): {}".format(address, message))

    @recv_op(Op.CONTROL, fmt='hh')
    def recv_control(self, left: int, right: int, address=None, **_):
        """
        Received a control command. Pass it along to the arduino.
        """
        # print("control received by {} from {}: {}, {}".format(self.id, address, left, right))
        self.bot.arduino.control(left, right)
