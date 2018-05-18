"""
Plots all information about bots onto a mpl basemap.
I really have no clue how i got this to work so please don't ask
"""

from tkinter import Frame
from mpl_toolkits.basemap import Basemap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


class GPSFrame(Frame):

    def __init__(self, bots):
        Frame.__init__(self)
        self.bots = bots
        print(self.bots)
        self.update_camera()

        fig = Figure()

        ax = plt.subplots(figsize=(15, 10))
        self.main_map = Basemap(resolution='c',
                                projection='cyl',
                                llcrnrlon=self.min_lon, llcrnrlat=self.min_lat,  # Lower left lat/lon
                                urcrnrlon=self.max_lon, urcrnrlat=self.max_lat)  # Upper right lat/lon

        self.main_map.readshapefile("resources/UScounties", "areas")
        self.main_map.shadedrelief()

        self.plot_bots()
        plt.show()

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().pack()

    # This method centers the camera around all bots.
    def update_camera(self):
        total_lon = 0
        total_lat = 0
        total_bots = len(self.bots)
        min_lon = 90
        min_lat = 90
        max_lon = -90
        max_lat = -90
        for bot_id in self.bots:
            bot = self.bots[bot_id]
            if min_lon > bot.lon:
                min_lon = bot.lon
            if min_lat > bot.lat:
                min_lat = bot.lat
            if max_lon < bot.lon:
                max_lon = bot.lon
            if max_lat < bot.lat:
                max_lat = bot.lat
            total_lon += bot.lon
            total_lat += bot.lat

        self.min_lon = min_lon
        self.max_lon = max_lon
        self.min_lat = min_lat
        self.max_lat = max_lat

        self.middle_lon = total_lon/total_bots
        self.middle_lat = total_lat/total_bots

        print("middle",self.middle_lon,self.middle_lat)
        print("min",self.min_lon,self.min_lat)
        print("max",self.max_lon,self.max_lat)

    def plot_bots(self):
        x,y = self.main_map(self.get_lons(), self.get_lats())
        self.points = self.main_map.plot(x, y, 'ro', markersize=6)
        for bot_id in self.bots:
            bot = self.bots[bot_id]
            plt.text(bot.lon, bot.lat, str(bot.id), fontsize=8)

    def update_bots(self, bots):
        self.bots = bots
        self.update_camera()
        #self.plot_bots()

    def get_lats(self):
        lats = []
        for bot_id in self.bots:
            bot = self.bots[bot_id]
            lats.append(bot.lat)
        return lats

    def get_ids(self):
        ids = []
        for bot_id in self.bots:
            bot = self.bots[bot_id]
            ids.append(bot.id)
        return ids

    def get_lons(self):
        lons = []
        for bot_id in self.bots:
            bot = self.bots[bot_id]
            lons.append(bot.lon)
        return lons
