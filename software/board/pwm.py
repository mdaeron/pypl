import pyb

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

