"""
Tests the xbee link
"""
import time
import random
import swarm

# load configuration
config1 = swarm.config.load()
config1['xbee']['port'] = 'COM7'
config1['arduino']['port'] = 'COM6'

config2 = swarm.config.load()
config2['xbee']['port'] = 'COM8'

bot = swarm.bot.Bot(config1)
n2 = swarm.communication.Network(bot, config2['xbee'])

print('name address')
print(bot.network.name, bot.network.id)
print(n2.name, n2.id)
print()

bot.start()
n2.start()

n2.send_debug('test')
while True:
    time.sleep(3)
    vals = [random.randrange(1, 200), random.randrange(1, 200)]
    print("Sending control signal: {}".format(vals))
    n2.send_control(*vals, address=b'\x00\x02')


