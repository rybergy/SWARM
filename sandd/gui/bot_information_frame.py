"""
Displays information about the bot.
"""
from tkinter import Frame, Label


class BotInformationFrame(Frame):

    def __init__(self, parent, bot):
        Frame.__init__(self, parent)
        self.bot = bot
        self.uuid_label = Label(self)
        self.uuid_label.pack()

        self.location_label = Label(self)
        self.location_label.pack()

        self.battery_label = Label(self)
        self.battery_label.pack()

        self.altitude_label = Label(self)
        self.altitude_label.pack()

        self.update()

    """
    Updates the information about the bot.
    """
    def update(self):
        self.uuid_label.config(text="BOT "+str(self.bot.id))
        self.location_label.config(text="GPS: "+str(self.bot.lat)+", "+str(self.bot.lon))
        self.battery_label.config(text="Battery: "+str(self.bot.battery)+"%")
        self.altitude_label.config(text="Altitude: "+str(self.bot.altitude)+" ft.")
