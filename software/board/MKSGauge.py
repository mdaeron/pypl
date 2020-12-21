import pyb, uasyncio

class MKSGauge() :

	def __init__(self, bus, baudrate = 230400, refresh = 0.25, start = True):
		self.bus = bus
		self.baudrate = baudrate
		self.refresh = refresh
		self.uart = pyb.UART(
			self.bus,
			baudrate = self.baudrate,
			bits = 8,
			parity = None,
			stop = 1,
			)
		self.P = None
		self.task = None
		if start: self.start()

	def write(self, msg):
		self.uart.write(('@254%s;FF' % msg).encode())

	def read(self):
		return self.uart.read().decode()
				
	async def loop(self):
		while True:
			try:
				self.P = float(self.read()[7:-3])
			except AttributeError:
				self.P = None
			self.write('PR4?')
			await uasyncio.sleep(self.refresh)

	def start(self):
		self.task = uasyncio.create_task(self.loop())

	def stop(self):
		self.task.cancel()
