"""
The window that opens once a bot's button is clicked.
Shows information about the bot as well as a control interface.
"""

from tkinter import Tk, Frame
from .bot_information_frame import BotInformationFrame
from .bot_control_frame import BotControlsFrame
from swarm.communication import Cycle
import time


class BotWindow(Tk):

    def __init__(self, bot):
        Tk.__init__(self)
        self.geometry("800x480")
        self.frame = Frame(self)
        self.frame.pack()
        self.bot = bot
        self.title("BOT "+str(self.bot.id))
        self.iconbitmap("resources/icon.ico")

        self.info_frame = BotInformationFrame(self, self.bot)
        self.info_frame.pack()
        self.controls_frame = BotControlsFrame(self, self.bot)
        self.controls_frame.pack()

    """
    Updates the information about the bot.
    """
    def update(self):
        self.info_frame.update()
        self.after(1000, self.update)
