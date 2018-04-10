from xbee import XBee
from serial import Serial
import numpy as np
from scipy.spatial import Voronoi


# represents point that has been sampled by a bot, known or communicated
class SampledPoint:
    def __init__(self, x, y, elevation):
        self.x = x
        self.y = y
        self.point = (self.x,self.y)
        self.elevation = elevation  # resource searching for

    def __repr__(self):
        return self, self.point, self.elevation


# creates and adds new point to known sampledPoints list
def addPoint(x, y, elevation, sampledPoints):
    sampledPoints.append(SampledPoint(x, y, elevation))


# send point to all known xbees in range
def broadcastNewPoint(point, connections):
    pass
    for bot in connections:
        sendXBeeMessage(bot, point)



def sendXBeeMessage(address, data):
    PORT = '/dev/ttyUSB0'
    BAUD = 9600
    ser = Serial(PORT, BAUD)
    xbee = XBee(ser)
    xbee.tx(dest_addr='\x00\x01', data=data)


# returns a point from vertices, ideally the nearest to current location
# do not return if x already in sampled, precision radius
def nextGoal(algorithm, curLocation, sampledPoints, localMax):
    if algorithm == voronoi:
        return voronoi(curLocation, sampledPoints, localMax)


# convert sampledPoints data into numPy array for voronoi
# considers vertices of voronoi ridges as new goals
# return nearest
def voronoi(curLocation, sampledPoints, localMax):
    numPoints = np.empty((0,2), int)
    for sampledPoint in sampledPoints:
        numPoints = np.append(numPoints, np.array([sampledPoint.point]), axis=0)
    vertices = Voronoi(numPoints).vertices
    return vertices[(np.abs(vertices-curLocation)).argmin()]


# test
sampledPoints = []
curLocation = (2, 4)
localMax = SampledPoint(10, 10, 100)
connections = []

addPoint(1, 2, 0, sampledPoints)
addPoint(3.5, 2.6, 0, sampledPoints)
addPoint(2, 5, 10, sampledPoints)
addPoint(4, 5, 6, sampledPoints)

goal = nextGoal(voronoi, curLocation, sampledPoints, localMax)
print(goal)
