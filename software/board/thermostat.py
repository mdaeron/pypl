import pyb, uasyncio, time

class _PWM():

	config = {
		'X7':  {'timer': 13, 'channel': 1, 'mode': pyb.Timer.PWM},
		'X8':  {'timer': 14, 'channel': 1, 'mode': pyb.Timer.PWM},
		'Y3':  {'timer':  4, 'channel': 3, 'mode': pyb.Timer.PWM},
		'Y4':  {'timer':  4, 'channel': 4, 'mode': pyb.Timer.PWM},
		'Y11': {'timer':  1, 'channel': 2, 'mode': pyb.Timer.PWM_INVERTED},
		'Y12': {'timer':  1, 'channel': 3, 'mode': pyb.Timer.PWM_INVERTED},
		}

	def __init__(self, pin, freq = 1):
		timer = _PWM.config[pin]['timer']
		channel = _PWM.config[pin]['channel']
		mode = _PWM.config[pin]['mode']
		self.pin = pyb.Pin(pin, pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
		self.timer = pyb.Timer(timer, freq = freq)
		self.channel = self.timer.channel(
			channel, pin = self.pin,
			mode = mode,
			)
		self.output(0)

	def output(self, p = None):
		if p is None:
			return self.channel.pulse_width_percent()
		self.channel.pulse_width_percent(p)

	def state(self):
		return self.pin.value()


class PID():
	def __init__(self,f_in, f_out, set_point = 0, Kp = 3., Ki = 0.01, Kd = 0.0, I_min = -50, I_max = 50, cycle = 1, invert = False):
		self.f_in = f_in
		self.f_out = f_out
		self.Kp = Kp
		self.Ki = Ki
		self.Kd = Kd
		self.inv = -1 if invert else 1
		self.P = 0.
		self.I = 0.
		self.D = 0.
		self.I_max = I_max
		self.I_min = I_min
		self.set_point = set_point
		self.prev_input = 0.
		self.current_input = 0.
		self.error = 0.
		self.output = 0.
		self.task = None
		self.cycle = cycle
		self.last_update = time.ticks_ms()
		self.running = False
		
	def update(self):
		self.current_update = time.ticks_ms()

		self.current_input = self.f_in()
		self.error = (self.set_point - self.current_input) * self.inv

		self.P = self.Kp * self.error
		self.D = self.Kd * (self.current_input - self.prev_input) / time.ticks_diff(self.current_update, self.last_update) * 1000
		self.I += self.Ki * self.error
		if self.I > self.I_max:
			self.I = self.I_max
		elif self.I < self.I_min:
			self.I = self.I_min

		self.output = self.P + self.I - self.D + 10
		if self.output > 100:
			self.output = 100
		elif self.output < 0:
			self.output = 0
		
		self.f_out(self.output)

		print(
			'current = %.2f, error = %.2f, PID = [%.1f, %.1f, %.1f] (%.1f)'
			% (self.current_input, -self.error, self.P, self.I, self.D, self.set_point)
			)
		
		self.last_update = self.current_update

	async def loop(self):
		while True:
			self.update()
			await uasyncio.sleep(self.cycle)

	def start(self):
		self.task = uasyncio.create_task(self.loop())
		self.running = True

	def stop(self):
		self.task.cancel()
		self.f_out(0)
		self.running = False

class Thermostat():
	def __init__(self, hot_pid = None, cold_pid = None, T0 = 20):
		self.hot_pid = hot_pid
		self.cold_pid = cold_pid
		self.target = None
		self.T0 = T0

	def start(self, T):
		self.target = T

		if T < self.T0:
			pid, other_pid = self.cold_pid, self.hot_pid
		else:
			pid, other_pid = self.hot_pid, self.cold_pid

		if other_pid.running:
			other_pid.stop()

		pid.set_point = T
		if not pid.running:
			pid.start()
		
	def stop(self):
		self.target = None
		for pid in [self.hot_pid, self.cold_pid]:
			if pid.running:
				pid.stop()
