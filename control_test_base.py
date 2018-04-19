"""
Tests the xbee link
"""
import time
import random
import swarm
from collections import defaultdict

# load configuration
config = swarm.config.load()
config['xbee']['port'] = 'COM8'

n2 = swarm.communication.Network(None, config['xbee'])

n2.start()

while True:
    x = input()
    vals = defaultdict(lambda: [100, 100])
    vals.update({
        'w': [200, 200],
        'a': [150, 50],
        's': [0, 0],
        'd': [50, 150]
    })
    n2.send_control(*vals[x])
