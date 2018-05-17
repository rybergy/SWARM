from swarm.communication.network import Network
from swarm.communication import Cycle
from swarm.communication.link import recv_op, send_op
import swarm
from .bot import CommandBot


class SANDDNetwork(Network):

    def __init__(self):
        super(SANDDNetwork, self).__init__(None, swarm.config.load()['xbee'])
        self.bots = {}

    @Cycle.register(5)
    def update(self):
        self.send_req_status()

    @recv_op(Network.ReceiveOpType.STATUS, fmt='ifffi')
    def recv_status(self, bot_id: int, lat: float, lon: float, alt: float, battery: int):
        if id in self.bots:
            self.bots[bot_id].update_info(lat, lon, alt, battery)
        else:
            self.bots[bot_id] = CommandBot(self, bot_id, lat, lon, alt, battery)
