import ustruct, math, micropython, uasyncio

class MAX31855:
	def __init__(self, spi, cs, refresh = 0.25):
		self.refresh = refresh
		self.spi = spi
		self.spirecv = self.spi.recv
		self.cs = cs
		self.csv = self.cs.value
		self.data = bytearray(4)
# 		self.TR = None
# 		self.TAMB = None
# 		self.VOUT = None
# 		self.VREF = None
# 		self.VTOTAL = None
# 		self.TCOR = None
		self.task = None
		self.T = 0.
		self.start()
	
	@micropython.native
	def _read(self, both = True, internal = False, errorcheck = False):
		self.csv(0)
		try:
			self.spirecv(self.data)
		finally:
			self.csv(1)

		if errorcheck:
			if self.data[3] & 0x01:
				raise RuntimeError("thermocouple not connected")
			if self.data[3] & 0x02:
				raise RuntimeError("short circuit to ground")
			if self.data[3] & 0x04:
				raise RuntimeError("short circuit to power")
			if self.data[1] & 0x01:
				raise RuntimeError("faulty reading")

		temp, refer = ustruct.unpack('>hh', self.data)

		if both:
			refer >>= 4
			temp >>= 2
			return temp * 0.25, refer * 0.0625
		elif internal:
			refer >>= 4
			return refer * 0.0625
		else:
			temp >>= 2
			return temp * 0.25
		

	def _T(self):
		'''Approximate thermocouple temperature in degrees Celsius'''
		return self._read(both = False)

	def _Tcj(self):
		'''Cold junction temperature in degrees Celsius'''
		return self._read(both = False, internal = True)

	@micropython.native
	def T_NIST(self):
		'''
		Thermocouple temperature in degrees Celsius, computed using
		raw voltages and NIST approximation for Type K, see:
		https://srdata.nist.gov/its90/download/type_k.tab
		https://srdata.nist.gov/its90/type_k/kcoefficients_inverse.html
		'''

		TR, TAMB = self._read()

		# thermocouple voltage based on MAX31855's uV/degC for type K (table 1)
		VOUT = 0.041276 * (TR - TAMB)

		# cold junction equivalent thermocouple voltage (simple version)
# 		VREF = TAMB * 0.04073

		# cold junction equivalent thermocouple voltage (more accurate version)
		if TAMB >= 0:
			VREF = ( # takes 160 ms
				-0.176004136860e-01
				+ 0.389212049750e-01 * TAMB
				+ 0.185587700320e-04 * TAMB ** 2
				+ -0.994575928740e-07 * TAMB ** 3
				+ 0.318409457190e-09 * TAMB ** 4
				+ -0.560728448890e-12 * TAMB ** 5
				+ 0.560750590590e-15 * TAMB ** 6
				+ -0.320207200030e-18 * TAMB ** 7
				+ 0.971511471520e-22 * TAMB ** 8
				+ -0.121047212750e-25 * TAMB ** 9
				+ 0.1185976
				* math.exp(-0.1183432e-03 * (TAMB - 0.1269686e03) ** 2) # takes 25-30 ms
			)
		else:
			VREF = (
				0.394501280250e-01 * TAMB
				+ 0.236223735980e-04 * TAMB ** 2
				+ -0.328589067840e-06 * TAMB ** 3
				+ -0.499048287770e-08 * TAMB ** 4
				+ -0.675090591730e-10 * TAMB ** 5
				+ -0.574103274280e-12 * TAMB ** 6
				+ -0.310888728940e-14 * TAMB ** 7
				+ -0.104516093650e-16 * TAMB ** 8
				+ -0.198892668780e-19 * TAMB ** 9
				+ -0.163226974860e-22 * TAMB ** 10
			)

		# total thermoelectric voltage
		VTOTAL = VOUT + VREF

		# compute temperature
		if -5.891 <= VTOTAL <= 0: # T < 0 C
			TCOR = (
				2.5173462e01 * VTOTAL
				-1.1662878e00 * VTOTAL ** 2
				-1.0833638e00 * VTOTAL ** 3
				-8.9773540e-01 * VTOTAL * 4
				-3.7342377e-01 * VTOTAL ** 5
				-8.6632643e-02 * VTOTAL ** 6
				-1.0450598e-02 * VTOTAL ** 7
				-5.1920577e-04 * VTOTAL ** 8
				)
		elif 0 < VTOTAL <= 20.644: # 0 < T < 500 C
			TCOR = (
				2.508355e01 * VTOTAL
				+ 7.860106e-02 * VTOTAL ** 2
				- 2.503131e-01 * VTOTAL ** 3
				+ 8.315270e-02 * VTOTAL ** 4
				- 1.228034e-02 * VTOTAL ** 5
				+ 9.804036e-04 * VTOTAL ** 6
				- 4.413030e-05 * VTOTAL ** 7
				+ 1.057734e-06 * VTOTAL ** 8
				- 1.052755e-08 * VTOTAL ** 9
				)
		elif 20.644 < VTOTAL <= 54.886: # T > 500 C
			TCOR = (
				- 1.318058e02
				+ 4.830222e01 * VTOTAL ** 1
				- 1.646031e00 * VTOTAL ** 2
				+ 5.464731e-02 * VTOTAL ** 3
				- 9.650715e-04 * VTOTAL ** 4
				+ 8.802193e-06 * VTOTAL ** 5
				- 3.110810e-08 * VTOTAL ** 6
				)
		else:
			raise RuntimeError('Total thermoelectric voltage out of range: %.2f' % self.VTOTAL)
		return TCOR

	async def loop(self):
		while True:
			self.T = self.T_NIST()
			await uasyncio.sleep(self.refresh)

	def start(self):
		self.task = uasyncio.create_task(self.loop())

	def stop(self):
		self.task.cancel()
