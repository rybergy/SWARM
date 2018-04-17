"""
Tests the arduino serial link.
"""
import time
import random
import swarm

# load configuration
config = swarm.config.load()

bot = swarm.bot.Bot(config)
bot.start()

# main test
time.sleep(3)
bot.arduino.control(50, 75)
bot.arduino.new_gps(50.14063924666028, -90.94233550243678)
while bot.running:
    time.sleep(8)
    state: str = random.choice(['stop', 'forward', 'backward', 'left', 'right', 'auto'])
    print('STATE CHANGE: ' + state)
    bot.arduino.force_direction(state)

