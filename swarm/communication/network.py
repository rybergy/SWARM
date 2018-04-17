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

    # TODO: finish
