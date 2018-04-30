"""
Displays a list of all buttons to further invoke bot behavior.
"""

from tkinter import Button
from .scrollable_frame import ScrollableFrame
from .bot_window import BotWindow

BUTTON_HEIGHT = 5
BUTTON_WIDTH = 15


class BotListFrame(ScrollableFrame):

    def __init__(self, bots):
        ScrollableFrame.__init__(self)
        self.buttons = []
        self.bots = bots
        self.done = False
        self.add_bots(bots)

    """
    Takes all bots and makes a button for them. This button is bound to make a BotWindow with information about the bot.
    """
    def add_bots(self, bots):
        for bot_id in bots:
            bot = bots[bot_id]
            button = Button(self.interior, text="BOT "+str(bot.id), width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
            button.pack()
            button.bind("<Button-1>", self.open_bot)
            self.buttons.append(button)

    """
    Just updates the array to whatever the new bots are.
    """
    def update_bots(self, bots):
        self.bots = bots

    """
    Opens a bot window from a button's event object.
    """
    def open_bot(self, event):
        widget = event.widget
        index = 0
        for button in self.buttons:
            if widget == button:
                break
            index += 1
        a = BotWindow(self.bots[index])
        a.update()
