'''
Sync.py is intended to be a broadcast signal to share personal data 
with swarm

Current exists to send example message (datetime) to the hard coded 
xbee address x00x01
'''
from xbee import XBee
from serial import Serial
import datetime 

PORT = '/dev/ttyUSB0'
BAUD = 9600

ser = Serial(PORT, BAUD)

xbee = XBee(ser)

def main(): 
	print("sync.py")
	# Send the string 'Hello World' to the module with MY set to 1
	data = str(datetime.datetime.now())
	print("sending ", data, " to destination 0001")
	xbee.tx(dest_addr='\x00\x01', data=data)
