from threading import Thread

from sensormessage import SensorMsg
from sensor import Sensor


class PacketHandler(Thread):
    def __init__(self, sensors, am, defaultLocs):
        super(PacketHandler, self).__init__()
        self.am = am
        self.sensors = sensors
        self.beRunning = True
        self.defaultLocs = defaultLocs

    def run(self):
        types = {
            1 : "Light",
            2 : "Heat",
        }
        while self.beRunning:
            packet = self.am.read(1)
            if packet and packet.type == 0x8A:
                msg = SensorMsg(packet.data)
                if not msg.type in types:
                    continue
                sensor = str(msg.id)+" - "+types[msg.type]
                try:
                    self.sensors[sensor].append(msg)
                except KeyError:
                    pos = self.defaultLocs.get(msg.id, (-100, -100))
                    self.sensors[sensor] = Sensor(msg, pos)
