#! /usr/bin/env python3

from datetime import datetime
from numpy import sin, cos, arange, array, inf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.animation as animation
from matplotlib.widgets import CheckButtons
import sys

x = arange(20)/4

class LivePlot():

	def __init__(self, file):
		self.data = None
		self.fields = []
		self.file = file
		self.colors = 'rbgmkcy'
		self.fig = plt.figure()
		self.ax1 = self.fig.add_axes((.1,.55,.7,.35))
		self.ax2 = self.fig.add_axes((.1,.1,.7,.35), sharex = self.ax1)
		self.ax1.tick_params(axis = 'both', which = 'both',length = 4, color = '#00000040')
		self.ax2.tick_params(axis = 'both', which = 'both',length = 4, color = '#00000040')

		self.xlocator = mdates.AutoDateLocator(minticks=3, maxticks=7)
		self.xformatter = mdates.ConciseDateFormatter(self.xlocator)
		self.ax1.xaxis.set_major_locator(self.xlocator)
		self.ax1.xaxis.set_major_formatter(self.xformatter)

		self.fig.canvas.mpl_connect('key_press_event', self.press)
		self.readfile()
		for f in self.data:
			d = self.data[f]
			if d['yscale'] == 'lin':
				d['ax'] = self.ax1
				d['line'] = self.ax1.plot(d['x'], d['y'], '-', label = f, visible = d['visible'], color = d['color'])[0]
			elif d['yscale'] == 'log':
				d['ax'] = self.ax2
				d['line'] = self.ax2.semilogy(d['x'], d['y'], '-', label = f, visible = d['visible'], color = d['color'])[0]
		self.resize = {k: True for k in ['xmin', 'xmax', 'ymin', 'ymax']}

		self.rax = plt.axes([.84, .1, .15, .2], frameon = False)
		self.cb = CheckButtons( self.rax, [k for k in self.resize], [self.resize[k] for k in self.resize] )
		self.cb.on_clicked( self.fnx )


	def readfile(self):
		with open(self.file) as fid:
			data = [l.strip().split(',') for l in fid.readlines() if not l.startswith('# ')]
			self.fields = data[0]
			data = [{k:v if k == self.fields[0] else float(v) for k,v in zip(self.fields, l)} for l in data[1:]]
			if self.data is None:
				self.data = {
					f: dict(
						x = [datetime.strptime(r['Time'], '%Y-%m-%d %H:%M:%S.%f') for r in data],
						y = array([r[f] for r in data]),
						color = c,
						yscale = 'log' if f[0] == 'P' else 'lin',
						ax = self.ax2 if f[0] == 'P' else self.ax1,
						visible = True,
						line = None,
						)
					for c,f in zip(self.colors, self.fields[1:])
					}
			else:
				x = [datetime.strptime(r['Time'], '%Y-%m-%d %H:%M:%S.%f') for r in data]
				for f in self.fields[1:]:
					self.data[f]['x'] = x
					self.data[f]['y'] = array([r[f] for r in data])

	def fnx(self, cblabel):
		self.resize[cblabel] = not self.resize[cblabel]

	def press(self, event):
		if event.key in '1234567890'[:len(self.data)]:
			d = self.data[self.fields[1:]['1234567890'.index(event.key)]]
			d['visible'] = not d['visible']
			d['line'].set_visible(d['visible'])
		if 'alt' in event.key and event.key[-1] in '1234567890'[:len(self.data)]:
			d = self.data[self.fields[1:]['1234567890'.index(event.key[-1])]]
			d['yscale'] = 'log' if d['yscale'] == 'lin' else 'lin'
			d['ax'] = self.ax1 if d['yscale'] == 'lin' else self.ax2
		print(f'{event.key} done')

	def animation(self, i = 0):
		self.readfile()

		log_exist = 'log' in [v['yscale'] for v in self.data.values() if v['visible']]
		lin_exist = 'lin' in [v['yscale'] for v in self.data.values() if v['visible']]
		if log_exist and lin_exist:
			self.ax1.set_position((.1,.55,.7,.35))
			self.ax2.set_position((.1,.1,.7,.35))
		elif lin_exist:
			self.ax1.set_position((.1,.1,.7,.8))
			self.ax2.set_position((1.1,1.1,.7,.35))
		elif log_exist:
			self.ax2.set_position((.1,.1,.7,.8))
			self.ax1.set_position((1.1,1.1,.7,.8))

		self.ax1.lines = []
		self.ax2.lines = []

		for f in self.data:
			d = self.data[f]
			d['line'].set_data(d['x'], d['y'])
			if d['yscale'] == 'lin':
				d['ax'] = self.ax1
				d['line'] = self.ax1.plot(d['x'], d['y'], '-', label = f, visible = d['visible'], color = d['color'])[0]
			elif d['yscale'] == 'log':
				d['ax'] = self.ax2
				d['line'] = self.ax2.semilogy(d['x'], d['y'], '-', label = f, visible = d['visible'], color = d['color'])[0]

		if lin_exist:
			self.ax1.legend(loc = 'upper left', bbox_to_anchor = (1.05, 1))
			self.ax1.grid(alpha = .25)
		if log_exist:
			self.ax2.legend(loc = 'upper left', bbox_to_anchor = (1.05, 1))
			self.ax2.grid(alpha = .25)

		if lin_exist:
			if self.resize['xmin']:
				self.ax1.set_xlim(min([d['line'].get_xdata().min() for d in self.data.values() if d['visible'] and d['yscale'] == 'lin']), None)
			if self.resize['xmax']:
				self.ax1.set_xlim(None, max([d['line'].get_xdata().max() for d in self.data.values() if d['visible'] and d['yscale'] == 'lin']))
			if self.resize['ymin']:
				self.ax1.set_ylim(min([d['line'].get_ydata().min() for d in self.data.values() if d['visible'] and d['yscale'] == 'lin']), None)
			if self.resize['ymax']:
				self.ax1.set_ylim(None, max([d['line'].get_ydata().max() for d in self.data.values() if d['visible'] and d['yscale'] == 'lin']))
		if log_exist:
			if self.resize['xmin']:
				self.ax2.set_xlim(min([d['line'].get_xdata().min() for d in self.data.values() if d['visible'] and d['yscale'] == 'log']), None)
			if self.resize['xmax']:
				self.ax2.set_xlim(None, max([d['line'].get_xdata().max() for d in self.data.values() if d['visible'] and d['yscale'] == 'log']))
			if self.resize['ymin']:
				self.ax2.set_ylim(min([d['line'].get_ydata()[d['line'].get_ydata() > 0].min() for d in self.data.values() if d['visible'] and d['yscale'] == 'log']), None)
			if self.resize['ymax']:
				self.ax2.set_ylim(None, max([d['line'].get_ydata().max() for d in self.data.values() if d['visible'] and d['yscale'] == 'log']))

		self.ax1.xaxis.set_major_locator(self.xlocator)
		self.ax1.xaxis.set_major_formatter(self.xformatter)
		plt.draw()

	def start(self):
		self.ani = animation.FuncAnimation(self.fig, self.animation, interval = 1000)
		plt.show()

LivePlot(sys.argv[1]).start()


