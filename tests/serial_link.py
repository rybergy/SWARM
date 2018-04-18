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
bot.arduino.set_mode(0)
bot.arduino.control(50, 150)
time.sleep(1)
bot.arduino.control(200, 200)
time.sleep(2)
bot.arduino.control(25, 25)
time.sleep(2)
bot.arduino.control(0, 0)
bot.arduino.new_gps(50.14063924666028, -90.94233550243678)
while False:
    time.sleep(8)
    state: str = random.choice(['stop', 'forward', 'backward', 'left', 'right', 'auto'])
    print('DIRECTION CHANGE: ' + state)
    bot.arduino.force_direction(state)

