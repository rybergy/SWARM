"""
defines the main Bot class, which handles main program flow and accessing data between different systems.
"""

from swarm.communication import *


class Bot:
    """
    Houses all systems and shared data so they can interact.
    """

    def __init__(self, config):
        self.config = config
        # self.network = Network(self, config['xbee'])
        self.arduino = Arduino(self, self.config['arduino'])
        self.running = False

    def start(self):
        self.running = True
        # self.network.start()
        self.arduino.start()

    def stop(self):
        self.running = False
        # self.network.stop()
        self.arduino.stop()
