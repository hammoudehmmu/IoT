from tos import Packet


class SensorMsg(Packet):
    structure = [
        ('version',  'int', 2),
        ('filler', 'int', 1),
        ('ttl', 'int', 1),
        ('type', 'int', 1),
        ('id',       'int', 2),
        ('count',    'int', 1),
        ('readings', 'blob', None)
    ]

    def __init__(self, packet=None):
        Packet.__init__(self, SensorMsg.structure, packet)
        r = self.readings
        values = zip(r[0::2], r[1::2])  # repair uint_16
        self.readings = [(n[0]<<8)+n[1] for n in values]

