import pyb, uasyncio

class Heartbeat():
	def __init__(self, led = 3, cycle = 1, on = 0.4, max = 8, start = True):
		self.led = pyb.LED(led)
		self.cycle = cycle
		self.on = on
		self.off = 1 - on
		self.max = max
		self.delay = self.cycle * self.on / (2 * self.max - 1)
		self.task = None
		if start:
			self.start()
	
	async def loop(self):
		try:
			while True:
				await uasyncio.sleep(self.off * self.cycle)
				for x in range(self.max):
					self.led.intensity(2**(x+1) - 1)
					await uasyncio.sleep(self.delay)
				for x in range(self.max):
					if x:
						await uasyncio.sleep(self.delay)
					self.led.intensity(2**(self.max-x-1) - 1)
		except uasyncio.CancelledError:
			self.led.intensity(0)
			
	def start(self):
		self.task = uasyncio.create_task(self.loop())

	def stop(self):
		self.task.cancel()
