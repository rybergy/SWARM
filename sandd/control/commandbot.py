import random
from swarm.bot import Bot

DEGREE_SIGN= u'\N{DEGREE SIGN}'
random.seed(5)


class CommandBot(Bot):

    def move_forward(self):
        print(str(self.id) + " Move forward")

    def move_backward(self):
        print(str(self.id) + " Move backward")

    def turn_right(self):
        print(str(self.id) + " Turn right")

    def turn_left(self):
        print(str(self.id) + " Turn left")

    def stop_moving(self):
        print(str(self.id) + " Stop moving")
