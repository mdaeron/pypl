print('-- Booting uPyPL board --')

import pyb, uasyncio, utime, machine, math
from MKSGauge import MKSGauge
from max31865 import PT1000
from mcp23017 import MCP23017

class Valve():

	def __init__(self, gpio):
		self.gpio = gpio
	
	def state(self):
		return self.gpio.value()

	def open(self):
		self.gpio.value(1)

	def close(self):
		self.gpio.value(0)

	def toggle(self):
		self.gpio.value(1 - self.gpio.value())


class PyPL():

	def __init__(self, cycle = 0.01, separators = '\r;', status_cycle = 0.1, DEBUG = False):
		self.DEBUG = DEBUG
		self.serial = pyb.USB_VCP()
		self.cycle = cycle
		self.clock = 0
		self.rbuf = ''
		self.sep1, self.sep2 = separators
		self.instructions = []
		self.status_cycle = status_cycle
		self.task_blink = None

		self.i2c = machine.I2C(2)
		self.gpio = MCP23017(self.i2c, 0x20)
		self.gpio.mode = 0x0000 # configure all pins as outputs
		self.gpio.gpio = 0x0000 # set all pins to low

		self.pt1000_spi = machine.SoftSPI(
			baudrate = 100000,
			polarity = 0,
			phase = 1,
			bits = 8,
			firstbit = machine.SPI.MSB,
			sck = machine.Pin('Y6'),
			mosi = machine.Pin('Y7'),
			miso = machine.Pin('Y8'),
			)

# 		self.pt1000_spi = pyb.SPI(2,
# 			mode = pyb.SPI.MASTER,
# 			baudrate=100000,
# 			polarity=0,
# 			phase=1,
# 			bits = 8,
# 			firstbit = pyb.SPI.MSB)

		self.T1 = PT1000('X5', self.pt1000_spi)
# 		self.T2 = PT1000('X6', self.pt1000_spi)
# 		self.T3 = PT1000('X11', self.pt1000_spi)
# 		self.T4 = PT1000('X12', self.pt1000_spi)

		self.V1 = Valve(self.gpio[0])
		self.V2 = Valve(self.gpio[1])
		self.V3 = Valve(self.gpio[2])
		
		self.start_blink_dialog = 1

	def send(self, txt):
		self.serial.write(txt + self.sep1)

	def echo(self, txt):
		self.send('echo' + self.sep2 + txt)

	def zero_clock(self):
		self.send('zero_clock')

	def timestamped_echo(self, txt):
		self.send('timestamp')
		self.echo(txt)
	
	def newline(self):
		self.send('newline')
	
	def clearline(self):
		self.send('clearline')	

	def send_status(self):
		self.send(
			'status'
			+ self.sep2 + 'T1=f%.2f' % self.T1.T
			+ self.sep2 + 'V1=b%s' % self.V1.state()
			+ self.sep2 + 'V2=b%s' % self.V2.state()
			+ self.sep2 + 'V3=b%s' % self.V3.state()
			+ self.sep2 + 'start_blink_dialog=b%s' % self.start_blink_dialog
# 			+ self.sep2 + 'DEBUG=s%s' % repr(self.rbuf)
			)

	async def status_loop(self):
		while True:
			await uasyncio.sleep(self.status_cycle)
			self.send_status()
			

	async def loop(self):
		while True:
			self.clock = (self.clock + 1) % 100
			await uasyncio.sleep(self.cycle)

			# print debug info
			if self.DEBUG and self.clock == 0:
				print([self.rbuf], self.instructions)

			# read instructions from serial
			while self.serial.any():
				self.rbuf += self.serial.read().decode()
			if self.rbuf:
				self.instructions += self.rbuf.split(self.sep1)
				self.rbuf = self.instructions.pop()

			# process instructions
			while self.instructions:
				i = self.instructions.pop(0).split(self.sep2)
				if i[0] == 'toggle':
					self.__dict__[i[1]].toggle()
				elif i[0] == 'open':
					self.__dict__[i[1]].open()
				elif i[0] == 'close':
					self.__dict__[i[1]].close()
				elif i[0] == 'start':
					self.__dict__[i[1]].start()
				elif i[0] == 'stop':
					self.__dict__[i[1]].stop()
				elif i[0] == 'start_blink':
					self.task_blink = uasyncio.create_task(self.blink())
					
	async def countdown(self, t, txt = ' remaining...', dt = 1):
		clearline = False
		while t :
			if clearline:
				self.clearline()
			else:
				clearline = True
			self.echo('%02d:%02d%s' % (t // 60, t % 60, txt))
			await uasyncio.sleep(1)
			t -= dt
		self.clearline()

	def start(self):
		uasyncio.create_task(self.status_loop())
		uasyncio.run(self.loop())

	async def blink(self):
		try:
			self.start_blink_dialog = 0
			self.zero_clock()
			self.newline()
			self.timestamped_echo('Start blinking protocol')
			self.V1.close()
			self.V2.close()
			self.V3.close()
			self.timestamped_echo('Valves closed')
			await self.countdown(5)
			self.V1.open()
			self.V2.open()
			self.V3.open()
			self.timestamped_echo('Valves open')
			await uasyncio.sleep(1)
			self.timestamped_echo('End of blinking protocol')
			self.newline()
			self.start_blink_dialog = 1
		except uasyncio.CancelledError:
			self.newline()
			self.timestamped_echo('!!! Blinking protocol cancelled')
			self.newline()
		

if __name__ == '__main__':

	P = PyPL()
	P.start()
