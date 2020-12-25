import ustruct, math

class MAX31855:
	def __init__(self, spi, cs):
		self.spi = spi
		self.cs = cs
		self.data = bytearray(4)
		self.TR = None
		self.TAMB = None
		self.VOUT = None
		self.VREF = None
		self.VTOTAL = None
		self.TCOR = None

	def _read(self, internal = False):
		self.cs.value(0)
		try:
			self.spi.recv(self.data)
		finally:
			self.cs.value(1)
		if self.data[3] & 0x01:
			raise RuntimeError("thermocouple not connected")
		if self.data[3] & 0x02:
			raise RuntimeError("short circuit to ground")
		if self.data[3] & 0x04:
			raise RuntimeError("short circuit to power")
		if self.data[1] & 0x01:
			raise RuntimeError("faulty reading")
		temp, refer = ustruct.unpack('>hh', self.data)
		refer >>= 4
		temp >>= 2
		return refer * 0.0625 if internal else temp * 0.25

	def _T(self):
		'''Approximate thermocouple temperature in degrees Celsius'''
		return self._read()

	def _Tcj(self):
		'''Cold junction temperature in degrees Celsius'''
		return self._read(internal = True)

	def T(self):
		'''
		Thermocouple temperature in degrees Celsius, computed using
		raw voltages and NIST approximation for Type K, see:
		https://srdata.nist.gov/its90/download/type_k.tab
		'''
		self.TR = self._read()
		self.TAMB = self._read(internal = True)

		# thermocouple voltage based on MAX31855's uV/degC for type K (table 1)
		self.VOUT = 0.041276 * (self.TR - self.TAMB)

		# cold junction equivalent thermocouple voltage
		if self.TAMB >= 0:
			self.VREF = (
				-0.176004136860e-01
				+ 0.389212049750e-01 * self.TAMB
				+ 0.185587700320e-04 * self.TAMB ** 2
				+ -0.994575928740e-07 * self.TAMB ** 3
				+ 0.318409457190e-09 * self.TAMB ** 4
				+ -0.560728448890e-12 * self.TAMB ** 5
				+ 0.560750590590e-15 * self.TAMB ** 6
				+ -0.320207200030e-18 * self.TAMB ** 7
				+ 0.971511471520e-22 * self.TAMB ** 8
				+ -0.121047212750e-25 * self.TAMB ** 9
				+ 0.1185976
				* math.exp(-0.1183432e-03 * (self.TAMB - 0.1269686e03) ** 2)
			)
		else:
			self.VREF = (
				0.394501280250e-01 * self.TAMB
				+ 0.236223735980e-04 * self.TAMB ** 2
				+ -0.328589067840e-06 * self.TAMB ** 3
				+ -0.499048287770e-08 * self.TAMB ** 4
				+ -0.675090591730e-10 * self.TAMB ** 5
				+ -0.574103274280e-12 * self.TAMB ** 6
				+ -0.310888728940e-14 * self.TAMB ** 7
				+ -0.104516093650e-16 * self.TAMB ** 8
				+ -0.198892668780e-19 * self.TAMB ** 9
				+ -0.163226974860e-22 * self.TAMB ** 10
			)
		# total thermoelectric voltage
		self.VTOTAL = self.VOUT + self.VREF

		# determine coefficients
		# https://srdata.nist.gov/its90/type_k/kcoefficients_inverse.html
		if -5.891 <= self.VTOTAL <= 0:
			DCOEF = (
				0.0000000e00,
				2.5173462e01,
				-1.1662878e00,
				-1.0833638e00,
				-8.9773540e-01,
				-3.7342377e-01,
				-8.6632643e-02,
				-1.0450598e-02,
				-5.1920577e-04,
			)
		elif 0 < self.VTOTAL <= 20.644:
			DCOEF = (
				0.000000e00,
				2.508355e01,
				7.860106e-02,
				-2.503131e-01,
				8.315270e-02,
				-1.228034e-02,
				9.804036e-04,
				-4.413030e-05,
				1.057734e-06,
				-1.052755e-08,
			)
		elif 20.644 < self.VTOTAL <= 54.886:
			DCOEF = (
				-1.318058e02,
				4.830222e01,
				-1.646031e00,
				5.464731e-02,
				-9.650715e-04,
				8.802193e-06,
				-3.110810e-08,
			)
		else:
			raise RuntimeError(
				'Total thermoelectric voltage out of range: %.2f' % self.VTOTAL
			)
		# compute temperature
		self.TCOR = 0.
		for n, c in enumerate(DCOEF):
			self.TCOR += c * self.VTOTAL ** n
		return self.TCOR