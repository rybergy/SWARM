from serial import Serial
from xbee import XBee
from xbee.backend.base import TimeoutException

from .link import *


class Op(OpCode):
    DEBUG = b'\0'
    RECEIVED = b'\1'
    CONTROL = b'\2'
    STATUS = b'\3'
    REQUESTSTATUS = b'\4'


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

    def stop(self):
        super(Network, self).stop()
        self.serial.close()

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

    @recv_op(Op.DEBUG, fmt='STRING')
    def recv_debug(self, message: str, address=None, **_):
        """
        Received a debug message from another xbee.
        For now, simple stdout echo.
        """
        print("DEBUG from({}): {}".format(address, message))

    @send_op(Op.RECEIVED, fmt='NOTHING')
    def send_received(self):
        """
        Tell another Xbee that we received a valid packet.
        """
        # TODO

    @recv_op(Op.RECEIVED, fmt='NOTHING')
    def recv_received(self, **_):
        """
        Received a RECEIVE message from another xbee.
        """
        # TODO

    @send_op(Op.CONTROL, fmt='fff')
    def send_control(self, left: float, right: float, duration: float, address=None):
        """
        Send a control command to a specific address.
        If no address is specified, broadcasts to all.
        left and right are floats between +-1, percentages of max velocity for each side.
        duration is a float determining how long the command is run on the arduino (in seconds).
        """
        return Packet(left, right, duration, address=address)

    @recv_op(Op.CONTROL, fmt='fff')
    def recv_control(self, left: float, right: float, duration: float, **_):
        """
        Received a control command. Pass it along to the arduino.
        """
        self.hub.arduino.control(left, right, duration)

    @send_op(Op.STATUS, fmt='ifffi')
    def send_status(self):
        return Packet(
            int(self.id),
            self.hub.bot.lat, self.hub.bot.lon,
            self.hub.bot.alt, self.hub.bot.battery
        )

    @recv_op(Op.STATUS, fmt='ifffi')
    def recv_status(self, id: int, lat: float, lon: float, alt: float, battery: int):
        pass  # TODO

    @send_op(Op.REQUESTSTATUS, fmt='NOTHING')
    def send_req_status(self):
        return Packet()

    @recv_op(Op.REQUESTSTATUS, fmt='NOTHING')
    def recv_req_status(self, address=None, **_):
        self.send_status(address=address)
