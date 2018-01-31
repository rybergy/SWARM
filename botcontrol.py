#!/usr/bin/python
'''
Created by the ET Navswarm CS Team at the University of New Hampshire
Jake Branchaud, James Holden, Jordan Bates, Mohit Sagar
November 2017

Intended to be a high level control of a bot 
'''
import time
import start, moving, collavoid, sync, malfunction, stopped

#setup for asyncronous message listening 
import serial 
from xbee import XBee
serial_port = serial.Serial('/dev/ttyUSB0', 9600)

def print_data(data):
    """
    This method is called whenever data is received
    from the associated XBee device. Its first and
    only argument is the data contained within the
    frame.
    """
    print("\t", "Message Received: ", data)

xbee = XBee(serial_port, callback=print_data)
#/async

print("Bot code is begun.")

START = 0
MOVING = 1
COLL_AVOID = 2
SYNC = 3

STOPPED = -1
MALFUNCTION = -2

state = START

while state != MALFUNCTION and state != STOPPED:

    if state == START:
        print("Bot is in Starting state: sensors are initializing")
        start.main()
        time.sleep(1)
        state = MOVING

    elif state == MOVING:
        print("Bot is in Moving state")
        moving.main()
        time.sleep(1)
        state = COLL_AVOID

    elif state == COLL_AVOID:
        print("Bot is in Collision Avoidance state")
        stopped.main()
        time.sleep(1)
        state = SYNC

    elif state == SYNC:
        print("Bot is in Synchronizing state")
        sync.main()
        time.sleep(1)
        state = MOVING

if state == MALFUNCTION:
    print("Bot is in Out of Range/Malfunctioning state")
    malfunction.main()

if state == STOPPED:
    print("Bot is in Stopping state and is ready to be shut down")
    stopped.main()

#end async listen
xbee.halt()
serial_port.close()