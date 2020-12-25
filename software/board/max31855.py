import ustruct

class MAX31855:
    def __init__(self, spi, cs):
        self.spi = spi
        self.cs = cs
        self.data = bytearray(4)

    def read(self, internal=False):
        self.cs.value(0)
        try:
            self.spi.recv(self.data)
        finally:
            self.cs.value(1)
        if self.data[3] & 0x01:
            raise RuntimeError("thermocouple not connected")
        if self.data[3] & 0x02:
            raise RuntimeError("short circuit to ground")
        if self.data[3] & 0x04:
            raise RuntimeError("short circuit to power")
        if self.data[1] & 0x01:
            raise RuntimeError("faulty reading")
        temp, refer = ustruct.unpack('>hh', self.data)
        refer >>= 4
        temp >>= 2
        return refer * 0.0625 if internal else temp * 0.25
