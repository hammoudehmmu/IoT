from random import randint
from time import time, strftime
from pygame import Surface
from pygame.image import load

class Sensor(Surface):
    def __init__(self, msg, pos):
        count, parts = msg.count, msg.readings
        self.type = msg.type
        self.id = msg.id
        self.rerollColour()
        self.values = list([0 for n in range(400)])
        self.average = 0
        self.timestamp = time()
        self.last = -1
        self.anomaly = False
        self.idle = False
        self.position = pos
        self.report("Activated")
        self.append(msg)

    def report(self, reason, urgent=False):
        time = strftime("%H:%M:%S")
        if urgent:
            self.anomaly = (reason, time)
        else:
            self.anomaly = self.anomaly or (reason, time)
        return self.anomaly

    def checkAnomalous(self):
        window = 20
        self.average = sum(self.values[-window:])/window
        #stv = 0.005
        #lowBnd, upBnd = self.average*(1-stv), self.average*(1+stv)
        lowBnd, upBnd = self.average - 2, self.average + 2
        vals = self.values  # local variables accessed faster
        for n in vals[-window:-3]:
            if n < lowBnd or n > upBnd:
                delta = vals[-1]-vals[-window]
                if abs(delta) < 4:
                    self.report("Crossed")
                    return
                self.report("Increased" if delta>0 else "Decreased")
                return
        self.anomaly = False

    def append(self, msg):
        count, parts = msg.count, msg.readings
        if count == self.last or (count < self.last and count != 0):
            return
        newTimestamp = time()
        if (newTimestamp - self.timestamp) < 0.8:
            self.report("Collision")
        else:
            self.values = self.values[len(parts):] + parts
            if self.idle:
                self.anomaly = False
                self.idle = False                
                self.report("Activated")
            else:
                self.checkAnomalous()        
        self.timestamp = newTimestamp
        self.last = count

    def rerollColour(self):
        self.colour = tuple([randint(0, 200) for n in range(3)])

