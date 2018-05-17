"""
defines the main hub class, which handles main program flow and accessing data between different systems.
"""

from swarm.communication import *
from .bot import Bot


class Hub:
    """
    Houses all systems and shared data so they can interact.
    """

    def __init__(self, config):
        self.config = config
        self.network = Network(self, config['xbee'])
        self.arduino = Arduino(self, self.config['arduino'])
        self.running = False

        self.__data = {}

    def __getitem__(self, item):
        """Get existing bot data or create an empty one"""
        try:
            return self.__data[item]
        except KeyError:
            self.__data[item] = Bot(item, 0, 0, 95, 250)
            return self.__data[item]

    @property
    def bot(self):
        return self[self.network.id]

    def start(self):
        self.running = True
        self.network.start()
        self.arduino.start()

    def stop(self):
        self.running = False
        self.network.stop()
        self.arduino.stop()
