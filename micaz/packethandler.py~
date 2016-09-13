from threading import Thread

from sensormessage import SensorMsg
from sensor import Sensor


class PacketHandler(Thread):
    def __init__(self, sensors, am):
        super(PacketHandler, self).__init__()
        self.am = am
        self.sensors = sensors
        self.beRunning = True

    def run(self):
        types = {
            1 : "Light",
            2 : "Heat",        
        }
        while self.beRunning:
            packet = self.am.read(1)
            if packet and packet.type == 0x8A:
                msg = SensorMsg(packet.data)
                sensor = str(msg.id)+" - "+types[msg.type]
                try:
                    self.sensors[sensor].append(msg)
                except KeyError:
                    self.sensors[sensor] = Sensor(msg)

