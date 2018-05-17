import random

DEGREE_SIGN= u'\N{DEGREE SIGN}'
random.seed(5)


class Bot:

    def __init__(self, bot_id, lat, lon, battery, altitude):
        self.id = bot_id
        self.lat = lat
        self.lon = lon
        self.battery = altitude
        self.altitude = altitude

    def update_info(self, lat, lon, battery, altitude):
        self.lat = lat
        self.lon = lon
        self.battery = altitude
        self.altitude = altitude

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
