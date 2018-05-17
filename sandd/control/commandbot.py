import random
from swarm.bot import Bot

DEGREE_SIGN= u'\N{DEGREE SIGN}'
random.seed(5)


class CommandBot(Bot):

    def __init__(self, network, *args, **kwargs):
        self.network = network
        super(CommandBot, self).__init__(*args, **kwargs)

    def move_forward(self):
        print(str(self.id) + " Move forward")
        self.network.send_control(.50, .50, .25, address=self.id)

    def move_backward(self):
        print(str(self.id) + " Move backward")
        self.network.send_control(-.50, -.50, .25, address=self.id)

    def turn_right(self):
        print(str(self.id) + " Turn right")
        self.network.send_control(.50, -.50, .25, address=self.id)

    def turn_left(self):
        print(str(self.id) + " Turn left")
        self.network.send_control(-.50, .50, .25, address=self.id)

    def stop_moving(self):
        print(str(self.id) + " Stop moving")
        self.network.send_control(0, 0, .25, address=self.id)
