"""
data representing a bot.
"""


class Bot:
    def __init__(self, bot_id, lat, lon, battery, altitude):
        self.id = bot_id
        self.lat = lat
        self.lon = lon
        self.battery = battery
        self.altitude = altitude

    def update_info(self, lat, lon, battery, altitude):
        self.lat = lat
        self.lon = lon
        self.battery = battery
        self.altitude = altitude
