"""
Constructs the main SAND-D window.
Left frame is a list of bots, right frame is a GPS frame.
"""

from gui.bot_list_frame import BotListFrame
from gui.gps_frame import GPSFrame
from control.sand_d_network import SANDDNetwork
from tkinter import *

network = SANDDNetwork()
network.start()
bot_list = network.bots


class MainWindow(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.title("SAND-D")
        self.iconbitmap("resources/icon.ico")
        self.geometry("800x480")
        self.resizable(0, 0)

        self.left_frame = BotListFrame(bot_list)
        self.left_frame.pack(fill=Y, side=LEFT)

        # Disabled for now because it's really slow
        # self.right_frame = GPSFrame(bot_list)
        # self.right_frame.pack(side=RIGHT)


def update_gui():
    bot_list = network.bots
    a.left_frame.update_bots(bot_list)
    a.right_frame.update_bots(bot_list)
    a.after(1000, update_gui)


a = MainWindow()
a.after(1000, update_gui)
a.mainloop()
