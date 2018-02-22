"""
defines the main Bot class, which handles main program flow and accessing data between different systems.
"""

import asyncio

from swarm.communication import *


class Bot:
    """
    Houses all systems and shared data so they can interact.
    """

    def __init__(self, config):
        self.config = config
        self.network = Network(self, config['xbee'])
        self.arduino = Arduino(self, config['arduino'])
        self.running = True

        self.state = None
        self.desired_state = type(self.state)

    async def run(self):
        self.network.start()
        self.arduino.start()

        while self.running:
            await self.state.loop()
            await asyncio.sleep(1)
            if not isinstance(self.state, self.desired_state):
                self.state = self.desired_state.make_from(self.state)
