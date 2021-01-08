import pyb, math, uasyncio

class PT1000():

	# Read Addresses
	MAX31865_REG_READ_CONFIG  = 0x00
	MAX31865_REG_READ_RTD_MSB = 0x01
	MAX31865_REG_READ_RTD_LSB = 0x02
	MAX31865_REG_READ_HFT_MSB = 0x03
	MAX31865_REG_READ_HFT_LSB = 0x04
	MAX31865_REG_READ_LFT_MSB = 0x05
	MAX31865_REG_READ_LFT_LSB = 0x06
	MAX31865_REG_READ_FAULT	= 0x07

	# Write Addresses
	MAX31865_REG_WRITE_CONFIG  = 0x80
	MAX31865_REG_WRITE_HFT_MSB = 0x83
	MAX31865_REG_WRITE_HFT_LSB = 0x84
	MAX31865_REG_WRITE_LFT_MSB = 0x85
	MAX31865_REG_WRITE_LFT_LSB = 0x86

	# Configuration Register
	MAX31865_CONFIG_50HZ_FILTER = 0x01
	MAX31865_CONFIG_CLEAR_FAULT = 0x02
	MAX31865_CONFIG_3WIRE       = 0x10
	MAX31865_CONFIG_ONE_SHOT    = 0x20
	MAX31865_CONFIG_AUTO        = 0x40
	MAX31865_CONFIG_BIAS_ON     = 0x80

	def spi_write(self, buf, select = True, deselect = True):
		if select: self.CS(False)
		try:
			self.spi.send(buf)
		except AttributeError:
			self.spi.write(buf)
		if deselect: self.CS(True)

	def spi_read(self, n = 1, select = True, deselect = True):
		if select: self.CS(False)
		try:
			out = self.spi.recv(n)
		except AttributeError:
			out = self.spi.read(n)
		if deselect: self.CS(True)
		return out
		
	def __init__(self, spi, cs_pin, wires=2, refresh = 0.25):
		self.T = None
		self.refresh = refresh
		self.CS = pyb.Pin(cs_pin, mode=pyb.Pin.OUT)
		self.CS(True)
		self.spi = spi
		self.RefR = 4300.0
		self.R0  = 1000.0
		self.task = None

		config = 128+4+1

		config = self.MAX31865_CONFIG_BIAS_ON + self.MAX31865_CONFIG_AUTO + self.MAX31865_CONFIG_CLEAR_FAULT + self.MAX31865_CONFIG_50HZ_FILTER
		if (wires == 3):
			 config = config + MAX31865_CONFIG_3WIRE

		buf = bytearray(2)
		buf[0] = self.MAX31865_REG_WRITE_CONFIG
		buf[1] = config
		self.spi_write(buf)
		self.start()

	def r2t(self, raw):
		RTD = (raw * self.RefR) / 32768
		A = 3.908e-3
		B = -5.775e-7
		return (-A + math.sqrt(A*A - 4*B*(1-RTD/self.R0))) / (2*B), RTD

	def read(self):
		self.spi_write(bytes([0x01]), deselect = False)
		MSB = self.spi_read(1, select = False, deselect = False)
		LSB = self.spi_read(1, select = False)

		raw = (MSB[0] << 8) + LSB[0]
		raw = raw >> 1
		temp, RTD = self.r2t(raw)
		return temp if temp<500 else None

	async def loop(self):
		while True:
			self.T = self.read()
			await uasyncio.sleep(self.refresh)

	def start(self):
		self.task = uasyncio.create_task(self.loop())

	def stop(self):
		self.task.cancel()
