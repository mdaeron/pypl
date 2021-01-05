from pyb import micros, elapsed_micros

def timing(fun):
	def out(*args, **kwargs):
		start = micros()
		f = fun(*args, **kwargs)
		print('[%s] %.f us' % (fun.__name__, elapsed_micros(start)))
		return f
	return out
