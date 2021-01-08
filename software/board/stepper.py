import pyb, uasyncio

class Stepper():

	def __init__(self, stp_pin = 'X11', dir_pin = 'X12', fwd_dir = 0, resolution = 1600, inc_length = 1600//4, inc_duration = 1., start = True):
		self.stp_pin = pyb.Pin(stp_pin, pyb.Pin.OUT_PP)
		self.dir_pin = pyb.Pin(dir_pin, pyb.Pin.OUT_PP)
		self.fwd_dir = fwd_dir
		self.resolution = resolution
		self.inc_length = inc_length
		self.inc_duration = inc_duration
		self.delay = self.inc_duration / self.inc_length / 2
		self.stp_pin.value(0)
		self.dir_pin.value(self.fwd_dir)
		self.position = 0
		self.target = 0
		if start:
			self.start()

	async def loop(self):
		while True:
			if self.position != self.target:
				if self.target > self.position:
					self.dir_pin.value(self.fwd_dir)
				else:
					self.dir_pin.value(1-self.fwd_dir)
				self.stp_pin.value(1 - self.stp_pin())
				if self.stp_pin.value():
					if self.dir_pin.value() == self.fwd_dir:
						self.position = self.position + 1
					else:
						self.position = self.position - 1
			await uasyncio.sleep(self.delay)

	def start(self):
		uasyncio.create_task(self.loop())

	def fwd(self, n = 1):
		self.target = self.target + self.inc_length * n

	def bwd(self, n = 1):
		self.target = self.target - self.inc_length * n

	def microfwd(self, n = 1):
		self.target = self.target + n

	def microbwd(self, n = 1):
		self.target = self.target - n
