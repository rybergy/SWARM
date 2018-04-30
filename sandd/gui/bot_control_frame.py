"""
Shows arrow keys to remote-control a bot.
"""

from tkinter import Frame, Button

BUTTON_SIZE = 10


class BotControlsFrame(Frame):

    def __init__(self, parent, bot):
        Frame.__init__(self, parent)
        self.bot = bot
        self.button_right = Button(self, text=">", width=BUTTON_SIZE, height=BUTTON_SIZE)
        self.button_right.grid(row=1, column=2)
        self.button_right.bind("<ButtonPress-1>", self.right)
        self.button_right.bind("<ButtonRelease-1>", self.stop)

        self.button_left = Button(self, text="<", width=BUTTON_SIZE, height=BUTTON_SIZE)
        self.button_left.grid(row=1, column=0)
        self.button_left.bind("<ButtonPress-1>", self.left)
        self.button_left.bind("<ButtonRelease-1>", self.stop)

        self.button_up = Button(self, text="^", width=BUTTON_SIZE, height=BUTTON_SIZE)
        self.button_up.grid(row=0, column=1)
        self.button_up.bind("<ButtonPress-1>", self.forward)
        self.button_up.bind("<ButtonRelease-1>", self.stop)

        self.button_down = Button(self, text="∨", width=BUTTON_SIZE, height=BUTTON_SIZE)
        self.button_down.grid(row=1, column=1)
        self.button_down.bind("<ButtonPress-1>", self.backward)
        self.button_down.bind("<ButtonRelease-1>", self.stop)

    def right(self, event):
        self.bot.turn_right()

    def left(self, event):
        self.bot.turn_left()

    def forward(self, event):
        self.bot.move_forward()

    def backward(self, event):
        self.bot.move_backward()

    def stop(self, event):
        self.bot.stop_moving()