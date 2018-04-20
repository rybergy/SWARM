"""
Tests the arduino serial link.
"""
import time
import random
import swarm

# load configuration
config = swarm.config.load()

a = swarm.communication.Arduino(None, config['arduino'])
a.start()

# main test
time.sleep(3)
a.set_mode(0)
a.control(-.5, 1.0, 1)
time.sleep(1)
a.control(1.0, 1.0, 1)
time.sleep(2)
a.control(-.75, -.75, 1)
time.sleep(2)
a.control(0.0, 0.0, 1)
a.new_gps(50.14063924666028, -90.94233550243678)
while False:
    time.sleep(8)
    state: str = random.choice(['stop', 'forward', 'backward', 'left', 'right', 'auto'])
    print('DIRECTION CHANGE: ' + state)
    a.force_direction(state)

time.sleep(5)  # delay to let backround threads finish processing the commands and let the arduino catch up
a.stop()

