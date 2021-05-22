print('-- Booting uPyPL board --')

import pyb, uasyncio, utime, machine, math
from sys import print_exception
from MKSGauge import MKSGauge
from max31865 import PT1000
from max31856 import MAX31856
from mcp23017 import MCP23017
from timing import timing
from stepper import Stepper
from thermostat import _PWM, Thermostat, PID
from heartbeat import Heartbeat

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


class DummySensor():
	def __init__(self):
		self.T = lambda : 0.
		self.P = 0.
		self.v = 0
	
	def value(self, *args):
		if args:
			self.v = args[0]
		else:
			return(self.v)

	def toggle(self):
		self.value(1 - self.value())


class PyPL():

	def __init__(self, cycle = 0.01, separators = '\r;', status_cycle = 0.1, DEBUG = False):
		self.DEBUG = DEBUG
		self.heartbeat = Heartbeat()
		self.serial = pyb.USB_VCP()
		self.cycle = cycle
		self.clock = 0
		self.rbuf = ''
		self.sep1, self.sep2 = separators
		self.instructions = []
		self.status_cycle = status_cycle
		self.task_blink = None
		self.rtc = pyb.RTC()
# 		self.accel = pyb.Accel()


		self.stepper = Stepper(dir_pin = 'B4') # use B4 because X12 is fried on my development pyboard


		self.P1 = DummySensor()
		self.P2 = DummySensor()
		self.P3 = DummySensor()
		self.P4 = DummySensor()

		self.T1 = DummySensor()
		self.T2 = DummySensor()
		self.T3 = DummySensor()
		self.T4 = DummySensor()

		self.V1 = Valve(DummySensor())
		self.V2 = Valve(DummySensor())
		self.V3 = Valve(DummySensor())
		self.V4 = Valve(DummySensor())
		self.V5 = Valve(DummySensor())
		self.V6 = Valve(DummySensor())
		self.V7 = Valve(DummySensor())
		self.V8 = Valve(DummySensor())
		self.V9 = Valve(DummySensor())
		self.V10 = Valve(DummySensor())
		self.V11 = Valve(DummySensor())
		self.V12 = Valve(DummySensor())
		self.V13 = Valve(DummySensor())
		self.V14 = Valve(DummySensor())
		self.V15 = Valve(DummySensor())
		self.V16 = Valve(DummySensor())

		self.P1 = MKSGauge(6)
# 		self.P2 = MKSGauge(4)
# 		self.P3 = MKSGauge(1)
# 		self.P4 = MKSGauge(2)

		try:
			self.i2c = machine.I2C(2)
			self.gpio = MCP23017(self.i2c, 0x20)
			self.gpio.mode = 0x0000 # configure all pins as outputs
			self.gpio.gpio = 0x0000 # set all pins to low

			self.V1 = Valve(self.gpio[0])
			self.V2 = Valve(self.gpio[1])
			self.V3 = Valve(self.gpio[2])
			self.V4 = Valve(self.gpio[3])
			self.V5 = Valve(self.gpio[4])
			self.V6 = Valve(self.gpio[5])
			self.V7 = Valve(self.gpio[6])
			self.V8 = Valve(self.gpio[7])
			self.V9 = Valve(self.gpio[8])
			self.V10 = Valve(self.gpio[9])
			self.V11 = Valve(self.gpio[10])
			self.V12 = Valve(self.gpio[11])
			self.V13 = Valve(self.gpio[12])
			self.V14 = Valve(self.gpio[13])
			self.V15 = Valve(self.gpio[14])
			self.V16 = Valve(self.gpio[15])

		except OSError:
			pass




		self.spi = pyb.SPI(2, mode = pyb.SPI.MASTER, baudrate = 10**7, phase = 1)
		self.T1 = MAX31856(self.spi, pyb.Pin('X5', pyb.Pin.OUT))
		self.T2 = MAX31856(self.spi, pyb.Pin('X6', pyb.Pin.OUT))
		self.T3 = MAX31856(self.spi, pyb.Pin('X17', pyb.Pin.OUT))
		self.T4 = MAX31856(self.spi, pyb.Pin('X18', pyb.Pin.OUT))

		self.hPWM_1 = _PWM('Y3')
		self.cPWM_1 = _PWM('Y4')
		self.hPWM_2 = _PWM('X7')
		self.cPWM_2 = _PWM('X8')
		self.hPWM_3 = _PWM('Y12')
		self.cPWM_3 = _PWM('Y11')

		self.hPID_1 = PID(
			self.T1.T,
			self.hPWM_1.output,
			set_point = 40,
			Kp = 1., Ki = 0.03, Kd = 0., I_min = -6, I_max = 6, cycle = 1)

		self.cPID_1 = PID(
			self.T1.T,
			self.cPWM_1.output,
			set_point = -80,
			Kp = 1., Ki = 0.03, Kd = 0., I_min = -6, I_max = 6, cycle = 1, invert = True)

		self.hPID_2 = PID(
			self.T2.T,
			self.hPWM_2.output,
			set_point = 40,
			Kp = 1., Ki = 0.03, Kd = 0., I_min = -6, I_max = 6, cycle = 1)

		self.cPID_2 = PID(
			self.T2.T,
			self.cPWM_2.output,
			set_point = -80,
			Kp = 1., Ki = 0.03, Kd = 0., I_min = -6, I_max = 6, cycle = 1, invert = True)

		self.hPID_3 = PID(
			self.T3.T,
			self.hPWM_3.output,
			set_point = 40,
			Kp = 1., Ki = 0.03, Kd = 0., I_min = -6, I_max = 6, cycle = 1)

		self.cPID_3 = PID(
			self.T3.T,
			self.cPWM_3.output,
			set_point = -80,
			Kp = 1., Ki = 0.03, Kd = 0., I_min = -6, I_max = 6, cycle = 1, invert = True)

		self.TS1 = Thermostat(self.hPID_1, self.cPID_1)
		self.TS2 = Thermostat(self.hPID_2, self.cPID_2)
		self.TS3 = Thermostat(self.hPID_3, self.cPID_3)
		
		self.start_blink_dialog = 1
		self.stop_blink_dialog = 0
		self.confirm_stop_blink_dialog = 0
		self.undo_stop_blink_dialog = 0

	def send(self, txt):
		self.serial.write(txt + self.sep1)

	def echo(self, txt):
		self.send('echo' + self.sep2 + txt)

	def echolog(self, txt):
		self.send('echolog' + self.sep2 + txt)

	def zero_clock(self):
		self.send('zero_clock')

	def timestamped_echo(self, txt):
		self.send('timestamp')
		self.echolog(txt)
	
	def newline(self):
		self.send('newline')
	
	def clearline(self):
		self.send('clearline')	

	def datetime(self):
		now = self.rtc.datetime()
		s = now[6] + (255-now[7])/255
		return ('NOW=s%04d-%02d-%02d' % now[:3]) + (' %02d:%02d:' % now[4:6]) + ('%06.3f' % s)
	
	def set_rtc(self, t):
		self.rtc.datetime(t) # t must be a tuple of ints: (year, month, day, weekday, hours, minutes, seconds, subseconds)

	def send_status(self):
		self.send(
			'status'
			+ self.sep2 + self.datetime()
# 			+ self.sep2 + 'x=f%.2f' % (self.accel.x() / 32)
# 			+ self.sep2 + 'y=f%.2f' % (self.accel.y() / 32)
# 			+ self.sep2 + 'z=f%.2f' % (self.accel.z() / 32)
			+ self.sep2 + ('P1=n' if self.P1.P is None else ('P1=f%.4e' % self.P1.P))
			+ self.sep2 + ('P2=n' if self.P2.P is None else ('P2=f%.4e' % self.P2.P))
			+ self.sep2 + ('P3=n' if self.P3.P is None else ('P3=f%.4e' % self.P3.P))
			+ self.sep2 + ('P4=n' if self.P4.P is None else ('P4=f%.4e' % self.P4.P))
			+ self.sep2 + ('T1=n' if self.T1.T() is None else ('T1=f%.2f' % self.T1.T()))
			+ self.sep2 + ('T2=n' if self.T2.T() is None else ('T2=f%.2f' % self.T2.T()))
			+ self.sep2 + ('T3=n' if self.T3.T() is None else ('T3=f%.2f' % self.T3.T()))
			+ self.sep2 + ('T4=n' if self.T4.T() is None else ('T4=f%.2f' % self.T4.T()))
			+ self.sep2 + 'V1=b%s' % self.V1.state()
			+ self.sep2 + 'V2=b%s' % self.V2.state()
			+ self.sep2 + 'V3=b%s' % self.V3.state()
			+ self.sep2 + 'V4=b%s' % self.V4.state()
			+ self.sep2 + 'V5=b%s' % self.V5.state()
			+ self.sep2 + 'V6=b%s' % self.V6.state()
			+ self.sep2 + 'V7=b%s' % self.V7.state()
			+ self.sep2 + 'V8=b%s' % self.V8.state()
			+ self.sep2 + 'V9=b%s' % self.V9.state()
			+ self.sep2 + 'V10=b%s' % self.V10.state()
			+ self.sep2 + 'V11=b%s' % self.V11.state()
			+ self.sep2 + 'V12=b%s' % self.V12.state()
			+ self.sep2 + 'V13=b%s' % self.V13.state()
			+ self.sep2 + 'V14=b%s' % self.V14.state()
			+ self.sep2 + 'V15=b%s' % self.V15.state()
			+ self.sep2 + 'V16=b%s' % self.V16.state()
			+ self.sep2 + 'hPWM1=b%s' % self.hPWM_1.state()
			+ self.sep2 + 'cPWM1=b%s' % self.cPWM_1.state()
			+ self.sep2 + 'hPWM2=b%s' % self.hPWM_2.state()
			+ self.sep2 + 'cPWM2=b%s' % self.cPWM_2.state()
			+ self.sep2 + 'hPWM3=b%s' % self.hPWM_3.state()
			+ self.sep2 + 'cPWM3=b%s' % self.cPWM_3.state()
			+ self.sep2 + ('TS1=n' if self.TS1.target is None else ('TS1=f%.0f' % self.TS1.target))
			+ self.sep2 + ('TS2=n' if self.TS2.target is None else ('TS2=f%.0f' % self.TS2.target))
			+ self.sep2 + ('TS3=n' if self.TS3.target is None else ('TS3=f%.0f' % self.TS3.target))
# 			+ self.sep2 + 'start_blink_dialog=b%s' % self.start_blink_dialog
# 			+ self.sep2 + 'stop_blink_dialog=b%s' % self.stop_blink_dialog
# 			+ self.sep2 + 'confirm_stop_blink_dialog=b%s' % self.confirm_stop_blink_dialog
# 			+ self.sep2 + 'undo_stop_blink_dialog=b%s' % self.undo_stop_blink_dialog
# 			+ self.sep2 + 'DEBUG=s%s %s' % (repr(self.stepper.position), repr(self.stepper.target))
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
				self.echo('Stepper position: %.0f' % self.stepper.position)

			# read instructions from serial
			while self.serial.any():
				self.rbuf += self.serial.read().decode()
			if self.rbuf:
				self.instructions += self.rbuf.split(self.sep1)
				self.rbuf = self.instructions.pop()

			# process instructions
			while self.instructions:
				i = self.instructions.pop(0)
				if len(i):
					if i[0] == '@':
						eval(i[1:])

# 				if i[0] == 'toggle':
# 					self.__dict__[i[1]].toggle()
# 				elif i[0] == 'open':
# 					self.__dict__[i[1]].open()
# 				elif i[0] == 'close':
# 					self.__dict__[i[1]].close()
# 				elif i[0] == 'start':
# 					self.__dict__[i[1]].start()
# 				elif i[0] == 'start_thermostat':
# 					self.__dict__[i[1]].start(float(i[2]))
# 				elif i[0] == 'stop':
# 					self.__dict__[i[1]].stop()
# 				elif i[0] == 'start_blink':
# 					self.task_blink = uasyncio.create_task(self.blink())
# 				elif i[0] == 'stop_blink':
# 					self.confirm_stop_blink_dialog = 1
# 					self.undo_stop_blink_dialog = 1
# 				elif i[0] == 'confirm_stop_blink':
# 					self.confirm_stop_blink_dialog = 0
# 					self.undo_stop_blink_dialog = 0
# 					self.task_blink.cancel()
# 				elif i[0] == 'undo_stop_blink':
# 					self.confirm_stop_blink_dialog = 0
# 					self.undo_stop_blink_dialog = 0
# 				elif i[0] == 'stepper':
# 					if i[1] == 'fwd':
# 						self.stepper.fwd()
# 					elif i[1] == 'bwd':
# 						self.stepper.bwd()
# 				elif i[0] == 'set_rtc':
# 					self.rtc.datetime(tuple([int(e) for e in i[1:]]))
					
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
		with open('errorlog.txt', 'w') as f:
			f.write('')
		uasyncio.create_task(self.status_loop())
		uasyncio.run(self.loop())

	async def blink(self):
		try:
			self.send('start_prep')
			self.start_blink_dialog = 0
			self.stop_blink_dialog = 1
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
			await self.countdown(5)
			self.timestamped_echo('End of blinking protocol')
			self.newline()
			self.stop_blink_dialog = 0
			self.start_blink_dialog = 1
		except uasyncio.CancelledError:
			self.newline()
			self.timestamped_echo('!!! Blinking protocol cancelled')
			self.newline()
			self.stop_blink_dialog = 0
			self.start_blink_dialog = 1
		self.send('end_prep')
		

if __name__ == '__main__':

	pyb.LED(2).on()
	try:
		pypl = PyPL(DEBUG = False)	
		pyb.LED(2).off()
		pypl.start()
	except Exception as e:
		print_exception(e, open('errorlog.txt', 'w'))
		pyb.LED(2).off()
		pyb.LED(3).off()
		while True:
			pyb.LED(1).toggle()
			utime.sleep(.2)
