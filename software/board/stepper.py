import pyb, uasyncio

class Stepper():

	def __init__(self, timer = 12, stp_pin = 'X11', dir_pin = 'X12', fwd_dir = 0, resolution = 3200, inc_length = 3200//4, inc_duration = 1., start = True):
		self.stp_pin = pyb.Pin(stp_pin, pyb.Pin.OUT_PP)
		self.dir_pin = pyb.Pin(dir_pin, pyb.Pin.OUT_PP)
		self.fwd_dir = fwd_dir
		self.resolution = resolution
		self.inc_length = inc_length
		self.inc_duration = inc_duration
		self.timer = pyb.Timer(timer, freq = 2 * self.inc_length / self.inc_duration)
		self.stp_pin.value(0)
		self.dir_pin.value(self.fwd_dir)
		self.position = 0
		self.target = 0
		if start:
			self.timer.callback(self.loop)

	def start(self):
		self.timer.callback(self.loop)

	def stop(self):
		self.timer.callback(None)

	def loop(self, t):
		if self.position != self.target:
			if self.target > self.position:
				self.dir_pin.value(self.fwd_dir)
			else:
				self.dir_pin.value(1-self.fwd_dir)
			self.stp_pin.value(1 - self.stp_pin.value())
			if self.stp_pin.value():
				if self.dir_pin.value() == self.fwd_dir:
					self.position = self.position + 1
				else:
					self.position = self.position - 1

	def fwd(self, n = 1):
		self.target = self.target + self.inc_length * n

	def bwd(self, n = 1):
		self.target = self.target - self.inc_length * n

	def microfwd(self, n = 1):
		self.target = self.target + n

	def microbwd(self, n = 1):
		self.target = self.target - n
