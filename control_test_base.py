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
    x = input('direction: ')
    vals = defaultdict(lambda: [100, 100])
    vals.update({
        'w': [200, 200],
        'a': [50, 150],
        's': [0, 0],
        'd': [150, 50]
    })
    print(vals[x])
    n2.send_control(*vals[x])





