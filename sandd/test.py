
"""
Test class - makes random bots and updates their info every second.
"""

from gui.bot_list_frame import BotListFrame
from control.commandbot import CommandBot
from gui.gps_frame import GPSFrame
from tkinter import *
import random
import threading
import time

bot_list = {}
for i in range(0, 20):
    bot_list[i] = CommandBot(None, i, i*3, i*5, i*2, i*5)


class MainWindow(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.title("SAND-D")
        self.iconbitmap("resources/icon.ico")
        self.geometry("800x480")
        self.resizable(0, 0)

        self.left_frame = BotListFrame(bot_list)
        self.left_frame.pack(fill=Y, side=LEFT)

        #Disabled for now because it's really slow
        self.right_frame = GPSFrame(bot_list)
        self.right_frame.pack(side=RIGHT)


def update_gui():
    for bot_id in bot_list:
        bot_list[bot_id].update_info(random.randrange(-90, 90), random.randrange(-90, 90),
                                     random.randrange(0, 500),
                                     random.randrange(0, 100))
    a.left_frame.update_bots(bot_list)
    a.right_frame.update_bots(bot_list)
    a.after(1000, update_gui)


a = MainWindow()
a.after(1000, update_gui)
a.mainloop()
