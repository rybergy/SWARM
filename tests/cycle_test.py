"""
test cycle code
"""

from swarm.communication.link import *


class CycleTest(Link):
    def read(self) -> Packet:
        pass

    def write(self, packet: Packet):
        pass

    @Cycle.register(4)
    def four(self):
        print("cycled - 4")

    @Cycle.register(1)
    def one(self):
        print("cycled - 1")


cycle_test = CycleTest(None, None)
print("starting...")
cycle_test.start()
print("started")
time.sleep(20)
print("stopping...")
cycle_test.stop()
print("completed")
