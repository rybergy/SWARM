from serial import Serial
from xbee import XBee

from .link import Link


class Network(Link):
    """
    Handles communication between bots.
    """

    def __init__(self, bot, config):
        super(Network, self).__init__(bot, config)
        self.serial = Serial(config['port'], config['baud'])
        self.xbee = XBee(self.serial)

    def __wait_for_read(self):
        """
        reads a data frame from the network.
        """
        frame = self.xbee.wait_read_frame()

    def __wait_for_write(self, data, address=None):
        """
        Writes data to a specific address if one is specified.
        If no address is specified, broadcast to the network.
        """
        self.xbee.tx(dest_addr=address, data=data)
