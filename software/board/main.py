print('-- Booting uPyPL board --')

import pyb, uasyncio, utime, machine, math
from MKSGauge import MKSGauge
from max31865 import PT1000
from mcp23017 import MCP23017

class Board():

	def __init__(self, sep = '\r\n', status_freq = 0.5):
		self.pulse_counter = 0
		self.serial = pyb.USB_VCP()
		self.status_freq = status_freq
		self.sep = sep
# 		self.pt1000_spi = machine.SoftSPI(
# 			baudrate = 100000,
# 			polarity = 0,
# 			phase = 1,
# 			bits = 8,
# 			firstbit = machine.SPI.MSB,
# 			sck = machine.Pin('Y6'),
# 			mosi = machine.Pin('Y7'),
# 			miso = machine.Pin('Y8'),
# 			)

# 		self.pt1000_spi = pyb.SPI(2,
# 			mode = pyb.SPI.MASTER,
# 			baudrate=100000,
# 			polarity=0,
# 			phase=1,
# 			bits = 8,
# 			firstbit = pyb.SPI.MSB)

# 		self.T1 = PT1000('X6', self.pt1000_spi)
# 		self.T2 = PT1000('X5', self.pt1000_spi)
# 		self.T3 = PT1000('X11', self.pt1000_spi)
# 		self.T4 = PT1000('X12', self.pt1000_spi)

# 		self.P1 = MKSGauge(1)
# 		self.P2 = MKSGauge(2)
# 		self.P3 = MKSGauge(4)
# 		self.P4 = MKSGauge(6)

# 		self.send('')

	def send(self, txt):
		self.serial.write(txt + self.sep)

	def echo(self, txt):
		self.send('echo,' + txt)

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
			'status,P1=%s,P2=%s,P3=%s,P4=%s,T1=%s,T2=%s,T3=%s,T4=%s'
			% (self.P1.P, self.P2.P, self.P3.P, self.P3.P, self.T1.T, self.T2.T, self.T3.T, self.T4.T)
			)

	def start(self):
		uasyncio.run(self.main_loop())


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


	async def blink(self):
		try:
			self.button_start = True
			self.zero_clock()
			self.newline()
			self.timestamped_echo('Start blinking protocol')
			for i in range(3):
				for k in range(3):
					pyb.LED(1+k).off()
				self.timestamped_echo('LEDs off')
				await self.countdown(5)
				for k in range(3):
					pyb.LED(1+k).on()
				self.timestamped_echo('LEDs on')
				await uasyncio.sleep(1)
			self.timestamped_echo('End of blinking protocol')
			self.newline()
			self.button_start = False
		except uasyncio.CancelledError:
			self.newline()
			self.timestamped_echo('!!! Blinking protocol cancelled')
			self.newline()
			self.button_start = False

	async def status_loop(self):
		while True:
			self.send_status()
			await uasyncio.sleep(self.status_freq)

	async def main_loop(self):
		led = pyb.LED(3)
		led.intensity(20)
		uasyncio.create_task(self.status_loop())
		while True:
			self.pulse_counter = (self.pulse_counter + 1) % 100
			if self.pulse_counter in [0,3]:
				led.intensity(20-led.intensity())
			
			line = ''
			await uasyncio.sleep(0.01)
			while self.serial.any():
				new = self.serial.read().decode()
				line += new
			if line and line[-1] == '/':
				line = line[:-1].split(';')
# 				self.echo(str(line))
				if line[0] == 'get_status':
					self.send_status()
				elif line[0] == 'led_toggle':
					for i in line[1:]:
						if i in '1234':
							pyb.LED(int(i)).toggle()
				elif line[0] == 'stepper_fwd':
					self.echo('stepper_fwd')
					uasyncio.create_task(self.stepper.fwd())
				elif line[0] == 'stepper_bwd':
					self.echo('stepper_bwd')
					uasyncio.create_task(self.stepper.bwd())
				elif line[0] == 'blink':
					self.task_blink = uasyncio.create_task(self.blink())
				elif line[0] == 'cancel_blink':
					self.task_to_cancel = self.task_blink
					self.ask_to_abort = True
					self.ask_to_undo = True
				elif line[0] == 'abort':
					self.task_to_cancel.cancel()
					self.ask_to_abort = False
					self.ask_to_undo = False
				elif line[0] == 'undo':
					self.ask_to_abort = False
					self.ask_to_undo = False
		

class PyPL():

	def __init__(self, cycle = 0.01, separators = '\r;', status_cycle = 0.1):
		self.serial = pyb.USB_VCP()
		self.cycle = cycle
		self.clock = 0
		self.rbuf = ''
		self.sep1, self.sep2 = separators
		self.instructions = []
		self.status_cycle = status_cycle

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

	def send(self, txt):
		self.serial.write(txt + self.sep1)

	def print_status(self):
		self.send(
			'status'
			+ self.sep2 + 'T1=%s' % self.T1.T
			+ self.sep2 + 'out1=%s' % self.gpio[0].value()
			+ self.sep2 + 'out2=%s' % self.gpio[1].value()
			)

	async def status_loop(self):
		while True:
			await uasyncio.sleep(self.status_cycle)
			self.print_status()
			

	async def loop(self):
		while True:
			self.clock = (self.clock + 1) % 100
			await uasyncio.sleep(self.cycle)

			# print debug info
			if self.clock == 0:
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
					p = self.gpio[int(i[1])-1]
					p.value(1 - p.value())
					
	def start(self):
		uasyncio.create_task(self.status_loop())
		uasyncio.run(self.loop())


if __name__ == '__main__':

	P = PyPL()
	P.start()
