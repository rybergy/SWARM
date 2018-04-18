"""
Tests the xbee link
"""
import time
import random
import swarm

# load configuration
config = swarm.config.load()
config['xbee']['port'] = 'COM8'

n2 = swarm.communication.Network(None, config['xbee'])

n2.start()

while True:
    time.sleep(3)
    vals = [random.randrange(1, 200), random.randrange(1, 200)]
    print("Sending control signal: {}".format(vals))
    n2.send_control(*vals, address=b'\x00\x02')


